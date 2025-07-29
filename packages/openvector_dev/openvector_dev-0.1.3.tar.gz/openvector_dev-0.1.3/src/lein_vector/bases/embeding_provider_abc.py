from typing import List
from abc import ABC, abstractmethod

class EmbeddingProviderABC(ABC):
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        ...

    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        ...