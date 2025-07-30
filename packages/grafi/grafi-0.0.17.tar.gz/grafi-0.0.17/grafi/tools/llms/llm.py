from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Generator
from typing import Optional
from typing import Self
from typing import TypeVar

from openinference.semconv.trace import OpenInferenceSpanKindValues
from pydantic import Field

from grafi.common.models.invoke_context import InvokeContext
from grafi.common.models.message import Message
from grafi.common.models.message import Messages
from grafi.common.models.message import MsgsAGen
from grafi.tools.tool import Tool
from grafi.tools.tool import ToolBuilder


class LLM(Tool):
    system_message: Optional[str] = Field(default=None)
    oi_span_type: OpenInferenceSpanKindValues = OpenInferenceSpanKindValues.LLM
    api_key: Optional[str] = Field(
        default=None, description="API key for the LLM service."
    )
    model: str = Field(
        default="",
        description="The name of the LLM model to use (e.g., 'gpt-4o-mini').",
    )
    chat_params: Dict[str, Any] = Field(default_factory=dict)

    structured_output: bool = Field(
        default=False,
        description="Whether the output is structured (e.g., JSON) or unstructured (e.g., plain text).",
    )

    @abstractmethod
    def stream(
        self,
        invoke_context: InvokeContext,
        input_data: Messages,
    ) -> Generator[Message, None, None]:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    async def a_stream(
        self,
        invoke_context: InvokeContext,
        input_data: Messages,
    ) -> MsgsAGen:
        yield []  # Too keep mypy happy
        raise NotImplementedError("Subclasses must implement this method.")

    def prepare_api_input(self, input_data: Messages) -> Any:
        """Prepare input data for API consumption."""
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            "system_message": self.system_message,
            "oi_span_type": self.oi_span_type.value,
        }


T_L = TypeVar("T_L", bound=LLM)


class LLMBuilder(ToolBuilder[T_L]):
    """Builder for LLM instances."""

    def api_key(self, api_key: Optional[str]) -> Self:
        self._obj.api_key = api_key
        return self

    def model(self, model: str) -> Self:
        self._obj.model = model
        return self

    def chat_params(self, params: Dict[str, Any]) -> Self:
        self._obj.chat_params = params
        if "response_format" in params:
            self._obj.structured_output = True
        return self

    def system_message(self, system_message: Optional[str]) -> Self:
        self._obj.system_message = system_message
        return self
