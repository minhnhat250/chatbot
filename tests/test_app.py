import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.chat import get_chat_service
from app.services.chat_service import ChatService
from app.getways.base import BaseGateway


class MockGateway(BaseGateway):
    def __init__(self, name: str, model_name: str):
        self.name = name
        self.model_name = model_name

    async def generate(self, prompt: str) -> str:
        return f"Phản hồi từ {self.name}: {prompt}"


def get_mock_service() -> ChatService:
    gateways = {
        "gemini": MockGateway("Gemini", "gemini-2.5-flash"),
        "deepseek": MockGateway("DeepSeek", "deepseek-v4-pro"),
    }
    return ChatService(gateways=gateways)


class TestChatApp(unittest.TestCase):
    def test_root_and_docs(self):
        with TestClient(app) as client:
            res = client.get("/")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["docs"], "/docs")

            # Swagger UI và OpenAPI schema
            docs_res = client.get("/docs")
            self.assertEqual(docs_res.status_code, 200)
            openapi_res = client.get("/openapi.json")
            self.assertEqual(openapi_res.status_code, 200)

    def test_models_catalog(self):
        with TestClient(app) as client:
            res = client.get("/models")
            self.assertEqual(res.status_code, 200)
            ids = {item["id"] for item in res.json()["models"]}
            self.assertIn("gemini", ids)
            self.assertIn("deepseek", ids)

    def test_rejects_empty_prompt(self):
        with TestClient(app) as client:
            for empty_prompt in ("", "   "):
                res = client.post("/chat", json={"prompt": empty_prompt, "model": "gemini"})
                self.assertEqual(res.status_code, 422)

    def test_rejects_unknown_model(self):
        with TestClient(app) as client:
            res = client.post("/chat", json={"prompt": "Xin chào", "model": "unknown_ai"})
            self.assertEqual(res.status_code, 400)
            self.assertIn("không được hỗ trợ", res.json()["detail"])

    def test_chat_with_mocked_gemini(self):
        app.dependency_overrides[get_chat_service] = get_mock_service
        try:
            with TestClient(app) as client:
                res = client.post("/chat", json={"prompt": "Chào bạn", "model": "gemini"})
                self.assertEqual(res.status_code, 200)
                data = res.json()
                self.assertEqual(data["provider"], "gemini")
                self.assertIn("Phản hồi từ Gemini: Chào bạn", data["answer"])
                self.assertEqual(data["model"], "gemini-2.5-flash")
        finally:
            app.dependency_overrides.clear()

    def test_chat_with_mocked_deepseek(self):
        app.dependency_overrides[get_chat_service] = get_mock_service
        try:
            with TestClient(app) as client:
                res = client.post("/chat", json={"prompt": "Chào bạn", "model": "deepseek"})
                self.assertEqual(res.status_code, 200)
                data = res.json()
                self.assertEqual(data["provider"], "deepseek")
                self.assertIn("Phản hồi từ DeepSeek: Chào bạn", data["answer"])
        finally:
            app.dependency_overrides.clear()

    def test_ask_ai_legacy_endpoint(self):
        app.dependency_overrides[get_chat_service] = get_mock_service
        try:
            with TestClient(app) as client:
                res = client.post("/ask_ai", json={"prompt": "Test legacy", "model": "gemini"})
                self.assertEqual(res.status_code, 200)
                self.assertIn("Phản hồi từ Gemini: Test legacy", res.json()["answer"])
        finally:
            app.dependency_overrides.clear()


if __name__ == "__main__":
    unittest.main()
