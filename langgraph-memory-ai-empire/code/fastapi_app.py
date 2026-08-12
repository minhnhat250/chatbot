"""Minimal conversation API with a per-thread ownership check."""

from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from chat_service import ChatService


app = FastAPI(title="LangGraph Memory Lab")
chat_service = ChatService()
thread_owners: dict[str, str] = {}


class CreateConversationRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)


class MessageRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=100_000)


def require_owner(thread_id: str, user_id: str) -> None:
    owner = thread_owners.get(thread_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    if owner != user_id:
        raise HTTPException(status_code=403, detail="Conversation owner mismatch.")


@app.post("/conversations", status_code=201)
def create_conversation(payload: CreateConversationRequest):
    thread_id = str(uuid4())
    thread_owners[thread_id] = payload.user_id
    return {"thread_id": thread_id, "user_id": payload.user_id}


@app.post("/conversations/{thread_id}/messages")
def send_message(thread_id: str, payload: MessageRequest):
    require_owner(thread_id, payload.user_id)
    answer = chat_service.ask(
        user_id=payload.user_id,
        thread_id=thread_id,
        message=payload.message.strip(),
    )
    return {"thread_id": thread_id, "answer": answer}


@app.get("/conversations/{thread_id}/messages")
def get_messages(thread_id: str, user_id: str):
    require_owner(thread_id, user_id)
    return {"thread_id": thread_id, "messages": chat_service.history(thread_id)}


@app.delete("/conversations/{thread_id}", status_code=204)
def delete_conversation(thread_id: str, user_id: str):
    require_owner(thread_id, user_id)
    chat_service.delete_thread(thread_id)
    del thread_owners[thread_id]
