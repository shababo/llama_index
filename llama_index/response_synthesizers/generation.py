from typing import Any, Optional, Sequence

from llama_index.callbacks.base import CallbackManager
from llama_index.indices.prompt_helper import PromptHelper
from llama_index.llm_predictor.base import BaseLLMPredictor
from llama_index.llms import LLM
from llama_index.prompts import BasePromptTemplate
from llama_index.prompts.default_prompts import DEFAULT_SIMPLE_INPUT_PROMPT
from llama_index.prompts.mixin import PromptDictType
from llama_index.response_synthesizers.base import BaseSynthesizer
from llama_index.service_context import ServiceContext
from llama_index.types import RESPONSE_TEXT_TYPE


class Generation(BaseSynthesizer):
    def __init__(
        self,
        llm: Optional[LLM] = None,
        llm_predictor: Optional[BaseLLMPredictor] = None,
        callback_manager: Optional[CallbackManager] = None,
        prompt_helper: Optional[PromptHelper] = None,
        simple_template: Optional[BasePromptTemplate] = None,
        streaming: bool = False,
        # deprecated
        service_context: Optional[ServiceContext] = None,
    ) -> None:
        super().__init__(
            llm=llm,
            llm_predictor=llm_predictor,
            callback_manager=callback_manager,
            prompt_helper=prompt_helper,
            service_context=service_context,
            streaming=streaming,
        )
        self._input_prompt = simple_template or DEFAULT_SIMPLE_INPUT_PROMPT

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {"simple_template": self._input_prompt}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "simple_template" in prompts:
            self._input_prompt = prompts["simple_template"]

    async def aget_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        **response_kwargs: Any,
    ) -> RESPONSE_TEXT_TYPE:
        # NOTE: ignore text chunks and previous response
        del text_chunks

        if not self._streaming:
            return await self._llm_predictor.apredict(
                self._input_prompt,
                query_str=query_str,
                **response_kwargs,
            )
        else:
            return self._llm_predictor.stream(
                self._input_prompt,
                query_str=query_str,
                **response_kwargs,
            )

    def get_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        **response_kwargs: Any,
    ) -> RESPONSE_TEXT_TYPE:
        # NOTE: ignore text chunks and previous response
        del text_chunks

        if not self._streaming:
            return self._llm_predictor.predict(
                self._input_prompt,
                query_str=query_str,
                **response_kwargs,
            )
        else:
            return self._llm_predictor.stream(
                self._input_prompt,
                query_str=query_str,
                **response_kwargs,
            )
