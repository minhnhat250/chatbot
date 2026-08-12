"""Combine a short-term checkpointer and long-term Store."""

from dataclasses import dataclass
from typing import Any

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore

from long_term_memory import load_profile, save_profile
from short_term_memory import _find_name


@dataclass(frozen=True)
class UserContext:
    user_id: str


class ChatService:
    def __init__(
        self,
        *,
        checkpointer: InMemorySaver | None = None,
        store: InMemoryStore | None = None,
    ) -> None:
        self.checkpointer = checkpointer or InMemorySaver()
        self.store = store or InMemoryStore()

        def call_model(state: MessagesState, runtime: Runtime[UserContext]) -> dict:
            user_id = runtime.context.user_id
            messages = state["messages"]
            latest = str(messages[-1].content)
            lowered = latest.lower()

            if "h\u00e3y nh\u1edb" in lowered and (name := _find_name(messages)):
                profile = load_profile(self.store, user_id)
                profile["name"] = name
                save_profile(self.store, user_id, profile)
                answer = f"T\u00f4i s\u1ebd nh\u1edb b\u1ea1n t\u00ean {name}."
            elif "t\u00f4i t\u00ean g\u00ec" in lowered:
                thread_name = _find_name(messages[:-1])
                profile_name = load_profile(self.store, user_id).get("name")
                name = thread_name or profile_name
                answer = f"B\u1ea1n t\u00ean {name}." if name else "T\u00f4i ch\u01b0a bi\u1ebft t\u00ean b\u1ea1n."
            else:
                answer = "T\u00f4i \u0111\u00e3 nh\u1eadn \u0111\u01b0\u1ee3c tin nh\u1eafn."

            return {"messages": [AIMessage(content=answer)]}

        builder = StateGraph(MessagesState, context_schema=UserContext)
        builder.add_node("call_model", call_model)
        builder.add_edge(START, "call_model")
        builder.add_edge("call_model", END)
        self.graph = builder.compile(
            checkpointer=self.checkpointer,
            store=self.store,
        )

    def ask(self, *, user_id: str, thread_id: str, message: str) -> str:
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config,
            context=UserContext(user_id=user_id),
        )
        return str(result["messages"][-1].content)

    def history(self, thread_id: str) -> list[dict[str, Any]]:
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = self.graph.get_state(config)
        return [
            {"role": message.type, "content": str(message.content)}
            for message in snapshot.values.get("messages", [])
        ]

    def delete_thread(self, thread_id: str) -> None:
        self.checkpointer.delete_thread(thread_id)
