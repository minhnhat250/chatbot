import os
import logging
from typing import Optional

from google import genai
from dotenv import load_dotenv


logger = logging.getLogger(__name__)
logging.basicConfig(
    level =  logging.INFO,
    format = "%(asctime)s-%(name)s - %(levelname)s - %(message)s"
)

env_path = os.path.join(os.path.dirname(__file__),"..",".env")
load_dotenv(env_path)

class GeminiGateway:
    def __init__ (
        self,
        api_key: Optional[str] =None,
        model_gemini :Optional[str] = None
    ) -> None:

        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.info("Không tìm thấy API Gemini")
            raise ValueError("Vui lòng cấp GEMINI_API_KEY vào env")
        self.model_gemini= os.getenv("GEMINI_MODEL_NAME","gemini-3.1-flash-lite")
        if not self.model_gemini:
            logger.info("Không tìm thấy model Gemini")
            raise ValueError("Vui lòng cấp GEMINI_MODEL_NAME vào env")
        self.client = genai.Client(api_key = self.api_key)
        logger.info("Có thể sử dụng model Gemini")

    async def test_call_api(self,prompt:str) -> str:
        try:
            logger.info("Đang gởi yêu cầu lên gemini")
            respone = await self.client.aio.models.generate_content(
                model = self.model_gemini,
                contents = prompt
            )
            content = respone.text
            logger.info("Đã nhận được phản hồi từ gemini")
            return content
        except Exception as e:
            logger.error(f"Lỗi trong quá trình gởi yêu cầu")
            raise

if __name__ == "__main__":
    import asyncio
    async def run_test():
        try:
            gemini  = GeminiGateway()
            prompt = "Xin chào bạn là ai, nói rỏ tên model của"
            result = await gemini.test_call_api(prompt)
            print(result)
        except Exception as e:
            print (f"Lỗi {e}")
            raise
    asyncio.run(run_test())




