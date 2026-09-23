"""
Lớp cơ sở (Interface/Base Class) cho các AI Gateway
===================================================
File này định nghĩa 'khuôn mẫu' chung cho mọi cổng kết nối AI (Gateway).
Dù là Google Gemini hay DeepSeek (hay bất kỳ AI nào sau này thêm vào),
tất cả đều phải tuân theo chuẩn này: có hàm `generate(prompt)` để nhận câu hỏi và trả về câu trả lời.
"""

from abc import ABC, abstractmethod


class BaseGateway(ABC):
    """
    Lớp trừu tượng (Abstract Base Class) đại diện cho một AI Gateway.
    Mọi AI Gateway kế thừa lớp này bắt buộc phải viết hàm `generate`.
    """

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """
        Gửi prompt (câu hỏi) đến mô hình AI và trả về kết quả dạng văn bản (text).

        :param prompt: Chuỗi câu hỏi hoặc yêu cầu của người dùng.
        :return: Chuỗi câu trả lời từ AI.
        """
        pass
