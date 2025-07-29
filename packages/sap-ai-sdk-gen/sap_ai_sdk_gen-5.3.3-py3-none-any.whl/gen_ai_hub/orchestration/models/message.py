from dataclasses import dataclass
from enum import Enum
from typing import Union, Optional, List

from gen_ai_hub.orchestration.models.base import JSONSerializable
from gen_ai_hub.orchestration.models.response import MessageToolCall


class Role(str, Enum):
    """
    Enumerates supported roles in LLM-based conversations.

    This enum defines the standard roles used in interactions with Large Language Models (LLMs).
    These roles are generally used to structure the input and distinguish between different parts of the conversation.

    Values:
        USER: Represents the human user's input in the conversation.
        SYSTEM: Represents system-level instructions or context setting for the LLM.
        ASSISTANT: Represents the LLM's responses in the conversation.
        TOOL: Represents a tool or function that the LLM can call.
        DEVELOPER: Represents the developer's input or instructions in the conversation.
    """

    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    TOOL = "tool"
    DEVELOPER = "developer"


@dataclass
class Message(JSONSerializable):
    """
    Represents a single message in a prompt or conversation template.

    This base class defines the structure for all types of messages in a prompt,
    including content and role.

    Args:
        role: The role of the entity sending the message.
        content: The text content of the message.
    """

    role: Union[Role, str]
    content: str

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
        }


class SystemMessage(Message):
    """
    Represents a system message in a prompt or conversation template.

    System messages typically provide context or instructions to the AI model.

    Args:
        content: The text content of the system message.
    """

    def __init__(self, content: str):
        super().__init__(role=Role.SYSTEM, content=content)


class UserMessage(Message):
    """
    Represents a user message in a prompt or conversation template.

    User messages typically contain queries or inputs from the user.

    Args:
        content: The text content of the user message.
    """

    def __init__(self, content: str):
        super().__init__(role=Role.USER, content=content)


class AssistantMessage(Message):
    """
    Represents an assistant message in a prompt or conversation template.

    Assistant messages typically contain responses or outputs from the AI model.

    Args:
        content: The text content of the assistant message.
        refusal: A string indicating refusal reason.
        tool_calls: A list of tool call objects.
    """

    def __init__(
            self,
            content: str,
            refusal: Optional[str] = None,
            tool_calls: Optional[List[MessageToolCall]] = None,
    ):
        super().__init__(role=Role.ASSISTANT, content=content)
        self.refusal = refusal
        self.tool_calls = tool_calls

    def to_dict(self):
        base = super().to_dict()
        if self.refusal is not None:
            base["refusal"] = self.refusal
        if self.tool_calls is not None:
            base["tool_calls"] = [tool_call.to_dict() for tool_call in self.tool_calls]
        return base


class ToolMessage(Message):
    def __init__(self, content: str, tool_call_id: str):
        super().__init__(role=Role.TOOL, content=content)
        self.tool_call_id = tool_call_id

    def to_dict(self):
        base = super().to_dict()
        base["tool_call_id"] = self.tool_call_id
        return base
