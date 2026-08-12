import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


logger = logging.getLogger(__name__)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class GeminiGateway:
    def __init__(self, api_key: str | None = None, model_name: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Chưa cấu hình GEMINI_API_KEY trong file .env.")
        self.model_name = model_name or os.getenv("GEMINI_MODEL_NAME", "gemini-3.5-flash")
        self.client = genai.Client(api_key=self.api_key)
        logger.info("Đã cấu hình Gemini với model %s", self.model_name)

    async def generate(self, prompt: str) -> str:
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        if not response.text:
            raise RuntimeError("Gemini trả về nội dung rỗng.")
        return response.text

    async def test_call_api(self, prompt: str) -> str:
        """Giữ tương thích với mã nguồn cũ."""
        return await self.generate(prompt)
