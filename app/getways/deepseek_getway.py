"""
Cổng kết nối DeepSeek AI (DeepSeek Gateway)
===========================================
File này chịu trách nhiệm:
1. Kết nối với DeepSeek thông qua thư viện `openai` (vì API của DeepSeek tương thích hoàn toàn chuẩn OpenAI).
2. Gửi câu hỏi của người dùng và nhận câu trả lời từ mô hình DeepSeek.
"""

import logging
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.getways.base import BaseGateway

logger = logging.getLogger(__name__)


class DeepSeekGateway(BaseGateway):
    """
    Lớp xử lý việc giao tiếp với DeepSeek AI.
    """

    def __init__(self) -> None:
        # Lấy thông số cấu hình từ file .env
        settings = get_settings()
        self.api_key = settings.deepseek_api

        # Kiểm tra xem người dùng đã cấu hình API Key của DeepSeek chưa
        if not self.api_key:
            raise ValueError("Chưa cấu hình DEEPSEEK_API trong file .env.")

        self.base_url = settings.deepseek_base_url
        self.model_name = settings.effective_deepseek_model
        self.max_output_tokens = settings.max_output_token

        # Khởi tạo client kết nối bất đồng bộ (AsyncOpenAI)
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        logger.info("Đã khởi tạo thành công DeepSeek Gateway với model: %s", self.model_name)

    async def generate(self, prompt: str) -> str:
        """
        Gửi prompt đến DeepSeek và nhận câu trả lời (bất đồng bộ).
        """
        # Gọi API chat completion chuẩn của OpenAI-compatible
        response = await self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=self.max_output_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        # Trích xuất nội dung tin nhắn phản hồi
        message = response.choices[0].message
        content = message.content

        # Kiểm tra nếu nội dung trả về rỗng
        if not content:
            raise RuntimeError("DeepSeek trả về nội dung rỗng.")

        return content
