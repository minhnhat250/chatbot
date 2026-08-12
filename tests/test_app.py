from fastapi.testclient import TestClient

import app as app_module


class FakeGateway:
    async def generate(self, prompt: str) -> str:
        return f"Trả lời: {prompt}"


def test_root_and_models():
    with TestClient(app_module.app) as client:
        assert client.get("/").status_code == 200
        response = client.get("/models")
        assert response.status_code == 200
        assert {item["id"] for item in response.json()["models"]} == {
            "deepseek",
            "gemini",
        }


def test_rejects_unknown_model():
    with TestClient(app_module.app) as client:
        response = client.post("/ask_ai", json={"prompt": "Xin chào", "model": "unknown"})
        assert response.status_code == 400


def test_ask_ai_with_gateway_stub():
    with TestClient(app_module.app) as client:
        client.app.state.gateways["gemini"] = FakeGateway()
        response = client.post(
            "/ask_ai", json={"prompt": "Xin chào", "model": "gemini"}
        )
        assert response.status_code == 200
        assert response.json()["answer"] == "Trả lời: Xin chào"


def test_rejects_empty_prompt():
    with TestClient(app_module.app) as client:
        for prompt in ("", "   "):
            response = client.post(
                "/ask_ai", json={"prompt": prompt, "model": "gemini"}
            )
            assert response.status_code == 422
