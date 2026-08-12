"""Key-value long-term memory namespaced by user_id."""

import sys
from typing import Any

from langgraph.store.memory import InMemoryStore


def profile_namespace(user_id: str) -> tuple[str, str, str]:
    return ("users", user_id, "profile")


def save_profile(store: InMemoryStore, user_id: str, profile: dict[str, Any]) -> None:
    store.put(profile_namespace(user_id), "main", profile)


def load_profile(store: InMemoryStore, user_id: str) -> dict[str, Any]:
    item = store.get(profile_namespace(user_id), "main")
    return dict(item.value) if item else {}


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    memory_store = InMemoryStore()
    save_profile(
        memory_store,
        "user-nhat",
        {
            "name": "Nh\u1eadt",
            "language": "Vietnamese",
            "answer_style": "t\u1eebng b\u01b0\u1edbc",
        },
    )
    print(load_profile(memory_store, "user-nhat"))
