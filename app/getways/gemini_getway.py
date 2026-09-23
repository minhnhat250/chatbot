"""
Cổng kết nối Google Gemini AI (Gemini Gateway)
==============================================
File này chịu trách nhiệm:
1. Kết nối với Google Gemini bằng thư viện chính thức `google-genai`.
2. Gửi câu hỏi của người dùng và nhận câu trả lời từ Gemini.
"""

import logging
from google import genai

from app.core.config import get_settings
from app.getways.base import BaseGateway

logger = logging.getLogger(__name__)


class GeminiGateway(BaseGateway):
    """
    Lớp xử lý việc giao tiếp với Google Gemini AI.
    """

    def __init__(self) -> None:
        # Lấy thông tin cấu hình từ file .env qua get_settings()
        settings = get_settings()
        self.api_key = settings.gemini_api_key

        # Kiểm tra xem người dùng đã cung cấp API Key chưa
        if not self.api_key:
            raise ValueError("Chưa cấu hình GEMINI_API_KEY trong file .env.")

        self.model_name = settings.gemini_model_name

        # Khởi tạo client kết nối của Google GenAI với API Key đã cung cấp
        self.client = genai.Client(api_key=self.api_key)
        logger.info("Đã khởi tạo thành công Gemini Gateway với model: %s", self.model_name)

    async def generate(self, prompt: str) -> str:
        """
        Gửi prompt đến Google Gemini và chờ kết quả trả về (chạy bất đồng bộ - async).
        """
        # Gọi API tạo nội dung của Gemini (sử dụng .aio để hỗ trợ async/await)
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        # Kiểm tra nội dung câu trả lời
        if not response.text:
            raise RuntimeError("Gemini trả về nội dung rỗng.")

        return response.text

    async def test_call_api(self, prompt: str) -> str:
        """
        Hàm phụ trợ để kiểm tra nhanh API (tương thích ngược).
        """
        return await self.generate(prompt)
