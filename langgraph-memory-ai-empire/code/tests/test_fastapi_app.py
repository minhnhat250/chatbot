from fastapi.testclient import TestClient

from fastapi_app import app


def test_conversation_flow_and_ownership():
    with TestClient(app) as client:
        created = client.post("/conversations", json={"user_id": "user-a"})
        assert created.status_code == 201
        thread_id = created.json()["thread_id"]

        response = client.post(
            f"/conversations/{thread_id}/messages",
            json={"user_id": "user-a", "message": "T\u00f4i t\u00ean Nh\u1eadt."},
        )
        assert response.status_code == 200

        forbidden = client.get(
            f"/conversations/{thread_id}/messages",
            params={"user_id": "user-b"},
        )
        assert forbidden.status_code == 403


def test_unknown_thread_returns_404():
    with TestClient(app) as client:
        response = client.get(
            "/conversations/not-found/messages",
            params={"user_id": "user-a"},
        )
        assert response.status_code == 404
