import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI


logger = logging.getLogger(__name__)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class DeepSeekGateway:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model_name: str | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("DEEPSEEK_API")
        if not self.api_key:
            raise ValueError("Chưa cấu hình DEEPSEEK_API trong file .env.")
        self.base_url = base_url or os.getenv("BASE_URL", "https://api.deepseek.com")
        self.model_name = model_name or os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
        self.max_output_tokens = int(os.getenv("MAX_OUTPUT_TOKENS", "8192"))
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        logger.info("Đã cấu hình DeepSeek với model %s", self.model_name)

    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=self.max_output_tokens,
            messages=[{"role": "user", "content": prompt}],
            extra_body={"thinking": {"type": "enabled"}},
            reasoning_effort="high",
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("DeepSeek trả về nội dung rỗng.")
        return content

    async def test_call_api(self, prompt: str, **_: object) -> str:
        """Giữ tương thích với mã nguồn cũ."""
        return await self.generate(prompt)


Deepseek = DeepSeekGateway
