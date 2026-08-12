"""The smallest graph: START -> call_model -> END."""

import sys

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, MessagesState, StateGraph


def call_model(state: MessagesState) -> dict:
    latest = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"\u0110\u00e3 nh\u1eadn: {latest}")]}


builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)
graph = builder.compile()


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = graph.invoke(
        {"messages": [{"role": "user", "content": "Xin ch\u00e0o LangGraph"}]}
    )
    print(result["messages"][-1].content)
