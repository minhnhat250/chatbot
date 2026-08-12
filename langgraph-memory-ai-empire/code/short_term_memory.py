"""Thread-scoped short-term memory with InMemorySaver."""

import sys

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph


def _find_name(messages: list[BaseMessage]) -> str | None:
    markers = ("t\u00f4i t\u00ean l\u00e0 ", "t\u00f4i t\u00ean ")
    for message in reversed(messages):
        if not isinstance(message, HumanMessage):
            continue
        normalized = str(message.content).strip()
        lowered = normalized.lower()
        for marker in markers:
            position = lowered.find(marker)
            if position >= 0:
                value = normalized[position + len(marker) :].strip(" .!?,")
                if value and "g\u00ec" not in value.lower():
                    return value
    return None


def deterministic_model(state: MessagesState) -> dict:
    """Replace a real LLM with rules to test memory deterministically."""
    messages = state["messages"]
    latest = str(messages[-1].content).lower()
    if "t\u00f4i t\u00ean g\u00ec" in latest:
        name = _find_name(messages[:-1])
        answer = f"B\u1ea1n t\u00ean {name}." if name else "T\u00f4i ch\u01b0a bi\u1ebft t\u00ean b\u1ea1n."
    else:
        name = _find_name(messages)
        answer = f"Ch\u00e0o {name}!" if name else "T\u00f4i \u0111\u00e3 nh\u1eadn \u0111\u01b0\u1ee3c tin nh\u1eafn."
    return {"messages": [AIMessage(content=answer)]}


def build_graph(checkpointer: InMemorySaver | None = None):
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", deterministic_model)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", END)
    return builder.compile(checkpointer=checkpointer or InMemorySaver())


def ask(graph, thread_id: str, text: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(
        {"messages": [{"role": "user", "content": text}]},
        config,
    )
    return str(result["messages"][-1].content)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    chat_graph = build_graph()
    print(ask(chat_graph, "thread-a", "T\u00f4i t\u00ean Nh\u1eadt."))
    print(ask(chat_graph, "thread-b", "T\u00f4i t\u00ean An."))
    print(ask(chat_graph, "thread-a", "T\u00f4i t\u00ean g\u00ec?"))
    print(ask(chat_graph, "thread-b", "T\u00f4i t\u00ean g\u00ec?"))
