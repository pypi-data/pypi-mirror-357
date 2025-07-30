from .llm import LLM
from .models.openai_service.gpt import GPT
from typing import Generator
from .steps.step import Step


class ClientLLM:
    def __init__(
        self,
        name="openai",
        model="gpt4o-mini",
        len_context: int = 10,
    ):
        # self.llm: LLM = GPT(model=model, max_history_len=len_context)
        self.llm: LLM = GPT(max_history_len=len_context)

    def __call__(self, query: str) -> Generator[Step]:
        return self.llm(query=query)
