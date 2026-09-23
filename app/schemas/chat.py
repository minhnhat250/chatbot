"""
Định nghĩa cấu trúc dữ liệu đầu vào và đầu ra (Schemas)
======================================================
File này sử dụng Pydantic để:
1. Xác thực (validate) dữ liệu người dùng gửi lên API xem có đúng định dạng không.
2. Chuẩn hóa dữ liệu trả về cho client (Streamlit, Web, Swagger UI...).
"""

from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints


class AskRequest(BaseModel):
    """
    Dữ liệu người dùng gửi lên khi muốn chat với AI.
    Ví dụ JSON gửi lên:
    {
        "prompt": "Thủ đô của Việt Nam là gì?",
        "model": "gemini"
    }
    """

    # prompt: Nội dung câu hỏi.
    # - strip_whitespace=True: Tự động xóa khoảng trắng thừa ở 2 đầu.
    # - min_length=1: Không cho phép gửi câu hỏi rỗng (nếu rỗng sẽ báo lỗi 422 Unprocessable Entity).
    # - max_length=100000: Giới hạn độ dài tối đa để tránh quá tải server.
    prompt: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=100000),
    ] = Field(
        ...,
        description="Nội dung câu hỏi hoặc yêu cầu gửi đến mô hình AI.",
        examples=["Xin chào! Hãy giới thiệu ngắn gọn về bạn."],
    )

    # model: Tên nhà cung cấp AI muốn hỏi ("gemini" hoặc "deepseek").
    # Mặc định nếu không truyền thì dùng "gemini".
    model: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ] = Field(
        default="gemini",
        description="Nhà cung cấp AI cần chat: 'gemini' hoặc 'deepseek'.",
        examples=["gemini", "deepseek"],
    )


class AskResponse(BaseModel):
    """
    Dữ liệu server trả về cho người dùng sau khi AI phản hồi.
    Ví dụ JSON trả về:
    {
        "answer": "Thủ đô của Việt Nam là Hà Nội.",
        "provider": "gemini",
        "model": "gemini-2.5-flash"
    }
    """

    answer: str = Field(description="Nội dung câu trả lời được sinh ra từ AI.")
    provider: str = Field(description="Tên nhà cung cấp đã xử lý yêu cầu (gemini hoặc deepseek).")
    model: str = Field(description="Tên model cụ thể đã thực thi câu hỏi.")
