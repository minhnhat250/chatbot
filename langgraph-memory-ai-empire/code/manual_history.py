"""Minimal example: the application owns its conversation history."""

from dataclasses import dataclass, field
import sys


Message = dict[str, str]


def fake_model(messages: list[Message]) -> str:
    """A deterministic model keeps the example independent from API keys."""
    latest = messages[-1]["content"].lower()
    if "t\u00f4i t\u00ean g\u00ec" in latest:
        for message in reversed(messages[:-1]):
            content = message["content"]
            marker = "T\u00f4i t\u00ean "
            if message["role"] == "user" and marker in content:
                return f"B\u1ea1n t\u00ean {content.split(marker, 1)[1].rstrip('.')} .".replace(" .", ".")
        return "T\u00f4i ch\u01b0a bi\u1ebft t\u00ean b\u1ea1n."
    return "T\u00f4i \u0111\u00e3 nh\u1eadn \u0111\u01b0\u1ee3c tin nh\u1eafn."


@dataclass
class ManualConversation:
    messages: list[Message] = field(default_factory=list)

    def ask(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        answer = fake_model(self.messages)
        self.messages.append({"role": "assistant", "content": answer})
        return answer


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    chat = ManualConversation()
    print(chat.ask("T\u00f4i t\u00ean Nh\u1eadt."))
    print(chat.ask("T\u00f4i t\u00ean g\u00ec?"))
