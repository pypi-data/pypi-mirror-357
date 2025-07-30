from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Self
from typing import TypeVar
from typing import Union

from openinference.semconv.trace import OpenInferenceSpanKindValues
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from grafi.common.events.topic_events.consume_from_topic_event import (
    ConsumeFromTopicEvent,
)
from grafi.common.models.base_builder import BaseBuilder
from grafi.common.models.command import Command
from grafi.common.models.default_id import default_id
from grafi.common.models.invoke_context import InvokeContext
from grafi.common.models.message import Messages
from grafi.common.models.message import MsgsAGen
from grafi.common.topics.topic_base import TopicBase
from grafi.common.topics.topic_expression import SubExpr
from grafi.common.topics.topic_expression import TopicExpr
from grafi.common.topics.topic_expression import evaluate_subscription
from grafi.common.topics.topic_expression import extract_topics


class Node(BaseModel):
    """Abstract base class for nodes in a graph-based agent system."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    node_id: str = default_id
    name: str
    type: str
    command: Optional[Command] = Field(default=None)
    oi_span_type: OpenInferenceSpanKindValues  # Simplified for example
    subscribed_expressions: List[SubExpr] = Field(default=[])  # DSL-based subscriptions
    publish_to: List[TopicBase] = Field(default=[])  # Topics to publish to

    _subscribed_topics: Dict[str, TopicBase] = {}

    def invoke(
        self,
        invoke_context: InvokeContext,
        node_input: List[ConsumeFromTopicEvent],
    ) -> Messages:
        """Invoke the node's operation. (Override in subclass)"""
        raise NotImplementedError("Subclasses must implement 'invoke'.")

    async def a_invoke(
        self,
        invoke_context: InvokeContext,
        node_input: List[ConsumeFromTopicEvent],
    ) -> MsgsAGen:
        """Invoke the node's operation. (Override in subclass)"""
        yield []  # Too keep mypy happy
        raise NotImplementedError("Subclasses must implement 'invoke'.")

    async def a_stream(
        self,
        invoke_context: InvokeContext,
        node_input: List[ConsumeFromTopicEvent],
    ) -> MsgsAGen:
        """Invoke the node's operation. (Override in subclass)"""
        raise NotImplementedError("Subclasses must implement 'invoke'.")

    def get_command_input(self, node_input: List[ConsumeFromTopicEvent]) -> Messages:
        """Combine inputs in a way that's suitable for this node. (Override in subclass)"""
        raise NotImplementedError("Subclasses must implement 'get_command_input'.")

    def can_invoke(self) -> bool:
        """
        Check if this node can invoke given which topics currently have new data.
        If ALL of the node's subscribed_expressions is True, we return True.
        :return: Boolean indicating whether the node should run.
        """
        if not self.subscribed_expressions:
            return True

        topics_with_new_msgs = set()

        # Evaluate each expression; if any is satisfied, we can invoke.
        for topic in self._subscribed_topics.values():
            if topic.can_consume(self.name):
                topics_with_new_msgs.add(topic.name)

        for expr in self.subscribed_expressions:
            if not evaluate_subscription(expr, list(topics_with_new_msgs)):
                return False

        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "subscribed_expressions": [
                expr.to_dict() for expr in self.subscribed_expressions
            ],
            "publish_to": [topic.to_dict() for topic in self.publish_to],
            "command": self.command.to_dict() if self.command else None,
        }


T_N = TypeVar("T_N", bound=Node)


class NodeBuilder(BaseBuilder[T_N]):
    """Inner builder class for workflow construction."""

    def oi_span_type(self, oi_span_type: OpenInferenceSpanKindValues) -> Self:
        self._obj.oi_span_type = oi_span_type
        return self

    def name(self, name: str) -> Self:
        self._obj.name = name
        return self

    def type(self, type: str) -> Self:
        self._obj.type = type
        return self

    def command(self, command: Command) -> Self:
        self._obj.command = command
        return self

    def subscribe(self, subscribe_to: Union[TopicBase, SubExpr]) -> Self:
        """
        Begin building a DSL expression. Returns a SubscriptionDSL.Builder,
        which the user can chain with:
            .subscribed_to(topicA).and_().subscribed_to(topicB).build()
        """
        if isinstance(subscribe_to, TopicBase):
            self._obj.subscribed_expressions.append(TopicExpr(topic=subscribe_to))
        elif isinstance(subscribe_to, SubExpr):
            self._obj.subscribed_expressions.append(subscribe_to)
        else:
            raise ValueError(
                f"Expected a Topic or SubExpr, but got {type(subscribe_to)}"
            )
        return self

    def publish_to(self, topic: TopicBase) -> Self:
        self._obj.publish_to.append(topic)
        return self

    def build(self) -> T_N:
        """Finalize the node and return it."""
        # Get all topics from subscription expressions recursively

        topics = {
            topic.name: topic
            for expr in self._obj.subscribed_expressions
            for topic in extract_topics(expr)
        }

        self._obj._subscribed_topics = topics
        return self._obj
