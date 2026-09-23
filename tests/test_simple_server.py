import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

from simple_server import app


class TestSimpleServer(unittest.TestCase):
    def test_root(self):
        with TestClient(app) as client:
            res = client.get("/")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["status"], "online")

    def test_models_catalog(self):
        with TestClient(app) as client:
            res = client.get("/models")
            self.assertEqual(res.status_code, 200)
            ids = {item["id"] for item in res.json()["models"]}
            self.assertIn("gemini", ids)
            self.assertIn("deepseek", ids)

    def test_rejects_empty_prompt(self):
        with TestClient(app) as client:
            res = client.post("/chat", json={"prompt": "  ", "model": "gemini"})
            self.assertEqual(res.status_code, 422)

    def test_rejects_unknown_model(self):
        with TestClient(app) as client:
            res = client.post("/chat", json={"prompt": "Xin chào", "model": "unknown_ai"})
            self.assertEqual(res.status_code, 400)
            self.assertIn("không được hỗ trợ", res.json()["detail"])

    @patch("simple_server.ask_gemini")
    def test_chat_gemini_mocked(self, mock_ask):
        async def mock_resp(p):
            return f"Mocked Gemini: {p}"
        mock_ask.side_effect = mock_resp

        with TestClient(app) as client:
            res = client.post("/chat", json={"prompt": "Chào bạn", "model": "gemini"})
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["provider"], "gemini")
            self.assertIn("Mocked Gemini: Chào bạn", data["answer"])

    @patch("simple_server.ask_deepseek")
    def test_chat_deepseek_mocked(self, mock_ask):
        async def mock_resp(p):
            return f"Mocked DeepSeek: {p}"
        mock_ask.side_effect = mock_resp

        with TestClient(app) as client:
            res = client.post("/ask_ai", json={"prompt": "Chào bạn", "model": "deepseek"})
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["provider"], "deepseek")
            self.assertIn("Mocked DeepSeek: Chào bạn", data["answer"])


if __name__ == "__main__":
    unittest.main()
