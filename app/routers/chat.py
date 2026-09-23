"""
Router xử lý API Chat (Chat Router)
===================================
File này định nghĩa các đường dẫn API (Endpoints) liên quan đến chat:
- `POST /chat`: Endpoint chính để gửi câu hỏi và nhận câu trả lời từ AI.
- `POST /ask_ai`: Endpoint phụ (alias) để tương thích với ứng dụng Streamlit và luồng cũ.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.chat import AskRequest, AskResponse
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)

# Khởi tạo APIRouter của FastAPI với tag "Chat AI" để gom nhóm đẹp trong tài liệu /docs
router = APIRouter(tags=["Chat AI"])

# Khởi tạo một đối tượng ChatService dùng chung
_chat_service = ChatService()


def get_chat_service() -> ChatService:
    """
    Hàm phụ thuộc (Dependency) trả về thể hiện của ChatService.
    FastAPI sử dụng hàm này qua `Depends(get_chat_service)` để dễ dàng thay thế (mock) khi chạy test.
    """
    return _chat_service


@router.post(
    "/chat",
    response_model=AskResponse,
    summary="Chat với Gemini hoặc DeepSeek",
    description="Nhận câu hỏi và tên mô hình từ client, gọi AI tương ứng và trả lời.",
)
async def chat_endpoint(
    payload: AskRequest,
    service: ChatService = Depends(get_chat_service),
) -> AskResponse:
    """
    Hàm xử lý khi người dùng gửi request đến endpoint `/chat`.
    """
    try:
        # Chuyển tiếp yêu cầu sang ChatService để xử lý
        return await service.chat(payload)

    except ValueError as exc:
        # Lỗi dữ liệu không hợp lệ (ví dụ: chọn model không hỗ trợ, thiếu API key...) -> Trả về mã lỗi 400
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        # Lỗi trong quá trình chạy (ví dụ: AI trả về rỗng, lỗi kết nối nhà mạng...) -> Trả về mã lỗi 502
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Bắt các lỗi bất ngờ khác để server không bị sập -> Ghi log và trả về mã lỗi 500
        logger.exception("Lỗi không mong muốn khi gọi ChatService")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Đã xảy ra lỗi khi kết nối với AI provider: {str(exc)}",
        ) from exc


@router.post(
    "/ask_ai",
    response_model=AskResponse,
    summary="Alias: Hỏi AI (/ask_ai)",
    description="Đường dẫn tương thích ngược với Streamlit, trỏ thẳng về cùng logic của /chat.",
)
async def ask_ai_endpoint(
    payload: AskRequest,
    service: ChatService = Depends(get_chat_service),
) -> AskResponse:
    """
    Endpoint `/ask_ai` tái sử dụng hoàn toàn hàm `chat_endpoint` để tránh lặp code.
    """
    return await chat_endpoint(payload, service)
