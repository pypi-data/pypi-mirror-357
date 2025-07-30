from typing import Any
from typing import Self

from grafi.common.models.command import Command
from grafi.common.models.command import CommandBuilder
from grafi.common.models.invoke_context import InvokeContext
from grafi.common.models.message import Message
from grafi.common.models.message import Messages
from grafi.common.models.message import MsgsAGen
from grafi.tools.llms.llm import LLM


class LLMStreamResponseCommand(Command):
    llm: LLM

    @classmethod
    def builder(cls) -> "LLMStreamResponseCommandBuilder":
        """
        Return a builder for LLMStreamResponseCommand.

        This method allows for the construction of an LLMStreamResponseCommand instance with specified parameters.
        """
        return LLMStreamResponseCommandBuilder(cls)

    def invoke(self, invoke_context: InvokeContext, input_data: Messages) -> Message:
        raise NotImplementedError("Method 'invoke' not implemented in stream command")

    async def a_invoke(
        self, invoke_context: InvokeContext, input_data: Messages
    ) -> MsgsAGen:
        async for message in self.llm.a_stream(invoke_context, input_data):
            yield message

    def to_dict(self) -> dict[str, Any]:
        return {"llm": self.llm.to_dict()}


class LLMStreamResponseCommandBuilder(CommandBuilder[LLMStreamResponseCommand]):
    """
    Builder for LLMStreamResponseCommand.
    """

    def llm(self, llm: LLM) -> Self:
        self._obj.llm = llm
        return self

    def build(self) -> LLMStreamResponseCommand:
        return self._obj
