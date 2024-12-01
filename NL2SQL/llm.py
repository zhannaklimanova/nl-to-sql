from abc import ABC, abstractmethod


class LLM(ABC):
    @abstractmethod
    def nlq_to_sql(self, nlq: str) -> str:
        pass
