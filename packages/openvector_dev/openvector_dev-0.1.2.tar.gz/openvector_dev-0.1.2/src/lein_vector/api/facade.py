from typing import Sequence, Union
from uuid import uuid4
from datetime import datetime, UTC

from lein_vector import ShortTermMemory, QdrantAdapter, MemoryManagerQdrant
from lein_vector.schemas.chunk import Chunk, ChunkPayload
from lein_vector.sentence_transformer import EmbeddingProviderGemini

class MemoryFacade:
    def __init__(self, short_term, memory_manager, embedder):
        self.short = short_term
        self.long = memory_manager
        self.embed = embedder
        self._msg_no: dict[int, int] = {}

    @classmethod
    async def from_qdrant(
        cls,
        host: str,
        port: int,
        collection: str,
        vector_size: int = 768,
        api_key: str | None = None,
        short_maxlen: int = 20,
    ) -> "MemoryFacade":
        """
        Создаёт MemoryFacade со всеми зависимостями:
        - ShortTermMemory(maxlen=short_maxlen)
        - EmbeddingProviderGemini(api_key)
        - QdrantAdapter(host, port, collection, vector_size) + init_collection()
        - MemoryManagerQdrant(adapter, embedder)
        """
        # 1. short-term
        short_mem = ShortTermMemory(maxlen=short_maxlen)

        # 2. эмбеддер
        embedder = EmbeddingProviderGemini(api_key=api_key)

        # 3. адаптер Qdrant
        adapter = QdrantAdapter(host, port, collection, vector_size)
        await adapter.init_collection()

        # 4. менеджер долгой памяти
        long_mem = MemoryManagerQdrant(adapter, embedder)

        # 5. возвращаем фасад
        return cls(short_mem, long_mem, embedder)

    async def step_user(self, user_id: int, user_msg: str, topk: int = 3, history_n: int = 20):
        self.short.add("user", user_msg)
        embedding = await self.embed.get_embedding(user_msg)
        long_memories = await self.long.retrieve_by_embedding(user_id, embedding, topk=topk)
        short_ctx = self.short.window(history_n)
        return {
            "short_term": short_ctx,
            "long_term": long_memories
        }

    async def step_user_oai(
        self,
        user_id: int,
        user_msg: str,
        *,
        topk: int = 3,
        history_n: int = 20,
    ) -> dict:
        """
        Полный шаг для OpenAI-совместимого вывода:
        1. Записывает сообщение пользователя в short-term.
        2. Достаёт релевантные чанки из long-term.
        3. Возвращает short-term уже в формате OpenAI.
        """
        data = await self.step_user(user_id, user_msg, topk=topk, history_n=history_n)
        data["short_term"] = self._to_openai(data["short_term"])
        data["long_term"] = self._chunk_texts(data["long_term"])
        return data

    @staticmethod
    def _to_openai(msgs: list[dict]) -> list[dict]:
        role_map = {"gf": "assistant"}          # «gf» → OpenAI «assistant»
        return [
            {"role": role_map.get(m["role"], m["role"]), "content": m["text"]}
            for m in msgs
        ]

    async def step_gf(
            self,
            user_id: int,
            gf_msg: str,
            *,
            block_size: int = 8,
            save_pair: bool = True,
    ):
        # 1) кладём ответ в short-term
        curr_no = self._msg_no.get(user_id, 0) + 1
        self._msg_no[user_id] = curr_no
        self.short.add("gf", gf_msg, extra={"msg_no": curr_no})

        # 2) если блок из 'block_size' сообщений готов → формируем long-term чанк
        if save_pair and len(self.short.window()) >= block_size:
            last_block = self.short.window(block_size)  # последние 8 сообщений
            block_text = "\n".join(m["text"] for m in last_block)

            # считаем embedding один раз
            vector = await self.embed.get_embedding(block_text)

            new_chunk = Chunk(
                chunk_id=uuid4(),
                user_id=user_id,
                chunk_type="type0",
                created_at=datetime.now(UTC),
                last_hit=datetime.now(UTC),
                hit_count=0,
                text=block_text,
                persistent=False,
                extra={"msg_no": curr_no},
            )
            await self.long.upsert_chunk_with_vector(user_id, new_chunk, vector)

            # (необязательно) можешь очистить short-term, если maxlen маленький
            # self.short.clear_until(block_size)  ← если нужен скользящий сдвиг

        # 3) при необходимости запускаем merge / maintenance
        if curr_no % 40 == 0:  # каждые 40 сообщений
            await self.long.merge_old_chunks(user_id, "type0", n=5)

    def get_short_term(self, n=10) -> list:
        return self.short.window(n)

    async def get_long_term(self, user_id: int, embedding: list[float], topk: int = 3) -> list:
        return await self.long.retrieve_by_embedding(user_id, embedding, topk)

    def add_to_short(self, role: str, text: str) -> None:
        self.short.add(role, text)

    async def add_to_long(self, user_id: int, chunk: Chunk) -> None:
        await self.long.upsert_chunk(user_id, chunk)

    @staticmethod
    def _chunk_texts(chunks: Sequence[Union[Chunk, ChunkPayload]]) -> list[str]:
        """Вернуть список текстов из любых Chunk/ChunkPayload."""
        return [c.text for c in chunks]
