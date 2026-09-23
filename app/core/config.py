"""
File cấu hình hệ thống (Configuration)
=====================================
File này chịu trách nhiệm:
1. Đọc các biến môi trường từ file `.env` (như API Key, tên model, base URL).
2. Cung cấp đối tượng `Settings` để toàn bộ server dùng chung một cách an toàn và tiện lợi.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Lớp cấu hình quản lý toàn bộ thông số của ứng dụng.
    Pydantic sẽ tự động tìm các giá trị tương ứng trong file `.env` hoặc biến môi trường hệ điều hành.
    """

    # --- Cấu hình cho DeepSeek ---
    deepseek_api: str = ""  # API Key của DeepSeek (lấy từ https://platform.deepseek.com)
    deepseek_model: str = "deepseek-v4-pro"  # Tên model mặc định
    deepseek_model_name: str = ""  # Tên model bổ sung (nếu người dùng đặt khác trong .env)
    deepseek_base_url: str = "https://api.deepseek.com"  # Địa chỉ API của DeepSeek
    max_output_token: int = 100000  # Số lượng token đầu ra tối đa

    # --- Cấu hình cho Google Gemini ---
    gemini_api_key: str = ""  # API Key của Gemini (lấy từ Google AI Studio)
    gemini_model_name: str = "gemini-2.5-flash"  # Tên model Gemini muốn dùng

    # Cấu hình nạp file .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Bỏ qua các biến lạ không khai báo trong class này
    )

    @property
    def effective_deepseek_model(self) -> str:
        """
        Lấy tên model DeepSeek thực tế đang ưu tiên sử dụng:
        Ưu tiên `deepseek_model_name` -> `deepseek_model` -> mặc định 'deepseek-chat'.
        """
        return self.deepseek_model_name or self.deepseek_model or "deepseek-chat"


@lru_cache
def get_settings() -> Settings:
    """
    Hàm lấy cấu hình (dùng `@lru_cache` để chỉ đọc file .env một lần duy nhất,
    những lần gọi sau sẽ lấy lại kết quả trong bộ nhớ đệm, giúp server chạy nhanh hơn).
    """
    return Settings()
