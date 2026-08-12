"""Long-context strategies: trimming and a simple running summary."""

from dataclasses import dataclass

from langchain_core.messages import BaseMessage
from langchain_core.messages.utils import (
    count_tokens_approximately,
    trim_messages,
)


def context_for_model(
    messages: list[BaseMessage],
    *,
    max_tokens: int = 2_000,
) -> list[BaseMessage]:
    """Create a short model view without deleting stored history."""
    return trim_messages(
        messages,
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=max_tokens,
        start_on="human",
        end_on=("human", "tool", "ai"),
        include_system=True,
    )


@dataclass(frozen=True)
class CompactedConversation:
    summary: str
    recent_messages: list[dict[str, str]]


def compact_deterministically(
    messages: list[dict[str, str]],
    *,
    keep_recent: int = 4,
) -> CompactedConversation:
    """Demonstrate compaction with rules; this is not an LLM summarizer."""
    if len(messages) <= keep_recent:
        return CompactedConversation("", messages.copy())

    old_messages = messages[:-keep_recent]
    facts: list[str] = []
    for message in old_messages:
        content = message["content"].strip()
        if message["role"] == "user" and content:
            facts.append(f"User said: {content}")
    summary = " ".join(facts[-5:])
    return CompactedConversation(summary, messages[-keep_recent:])
