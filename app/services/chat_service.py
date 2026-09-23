"""
Dịch vụ điều phối Chat (Chat Service)
=====================================
File này đóng vai trò là 'trung tâm điều phối' (Service Layer):
1. Nhận yêu cầu chat từ tầng API Router.
2. Xác định xem người dùng muốn gọi mô hình nào (Gemini hay DeepSeek).
3. Lấy Gateway tương ứng để gửi câu hỏi.
4. Nhận câu trả lời và đóng gói thành đối tượng `AskResponse` chuẩn để trả về.
"""

import logging
from typing import Optional, Dict

from app.getways.base import BaseGateway
from app.getways.gemini_getway import GeminiGateway
from app.getways.deepseek_getway import DeepSeekGateway
from app.schemas.chat import AskRequest, AskResponse

logger = logging.getLogger(__name__)


class ChatService:
    """
    Lớp quản lý logic chat tổng thể của hệ thống.
    """

    def __init__(self, gateways: Optional[Dict[str, BaseGateway]] = None):
        """
        Khởi tạo ChatService.
        - Có thể truyền sẵn danh sách `gateways` (rất hữu ích khi viết test mock).
        - Nếu không truyền, hệ thống sẽ tự khởi tạo gateway khi có yêu cầu đầu tiên.
        """
        self._gateways: Dict[str, BaseGateway] = gateways if gateways is not None else {}

    def get_gateway(self, provider_key: str) -> BaseGateway:
        """
        Lấy cổng kết nối (Gateway) tương ứng với tên nhà cung cấp AI.
        Nếu đã khởi tạo trước đó thì tái sử dụng để tiết kiệm tài nguyên.
        """
        # Nếu đã có trong danh sách thì dùng lại
        if provider_key in self._gateways:
            return self._gateways[provider_key]

        # Nếu chưa có thì khởi tạo mới dựa theo tên provider
        if provider_key == "gemini":
            gateway = GeminiGateway()
        elif provider_key == "deepseek":
            gateway = DeepSeekGateway()
        else:
            # Nếu người dùng gửi tên lạ không hỗ trợ
            raise ValueError(
                f"Model/Provider '{provider_key}' không được hỗ trợ. Hãy chọn 'gemini' hoặc 'deepseek'."
            )

        # Lưu lại vào danh sách để lần sau dùng tiếp
        self._gateways[provider_key] = gateway
        return gateway

    def _resolve_provider(self, model_input: str) -> str:
        """
        Nhận diện nhà cung cấp dựa trên chuỗi `model` mà người dùng gửi lên.
        Ví dụ: 'gemini-2.5-flash' -> 'gemini', 'deepseek-v4-pro' -> 'deepseek'.
        """
        lowered = model_input.strip().lower()
        if "gemini" in lowered:
            return "gemini"
        if "deepseek" in lowered:
            return "deepseek"
        return lowered

    async def chat(self, request: AskRequest) -> AskResponse:
        """
        Xử lý trọn vẹn một yêu cầu chat từ người dùng:
        1. Phân tích tên model.
        2. Lấy gateway phù hợp.
        3. Gửi prompt đến AI và nhận câu trả lời.
        4. Trả về kết quả hoàn chỉnh dạng AskResponse.
        """
        # Bước 1: Nhận diện provider ('gemini' hoặc 'deepseek')
        provider = self._resolve_provider(request.model)

        # Bước 2: Lấy gateway tương ứng
        gateway = self.get_gateway(provider)

        # Bước 3: Gửi prompt đến AI
        logger.info("Đang gửi prompt đến provider '%s'...", provider)
        answer = await gateway.generate(request.prompt)

        # Bước 4: Lấy tên model cụ thể từ gateway (nếu có)
        model_name = getattr(gateway, "model_name", provider)

        # Bước 5: Đóng gói và trả về
        return AskResponse(
            answer=answer,
            provider=provider,
            model=model_name,
        )
