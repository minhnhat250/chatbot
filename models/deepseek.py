import os
import logging
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import List, Optional, Any, Dict

logger = logging.getLogger(__name__)
#Logging sẽ có các mức: debug, info, warning, error

logging.basicConfig(
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s -%(name)s - %(message)s"
)
load_env = os.path.join(os.path.dirname(__file__),'..','.env')
load_dotenv(load_env)

#Để kết nối được với deepseek API, ta cần: API_kEY, Base_URL, Model_name
class Deepseek:
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API")
        if not self.api_key:
            logger.error("API không tồn tại. Vui lòng kiểm tra")
        else:
            logger.info("Kết nối API thành công")

        self.base_url = base_url or os.getenv("BASE_URL", "https://api.deepseek.com")
        if not self.base_url:
            logger.error("Base URL không tồn tại. Vui lòng kiểm tra")
        else:
            logger.info("Kết nối Base URL thành công")

        self.model_name = model_name or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        if not self.model_name:
            logger.error("Model name không tồn tại. Vui lòng kiểm tra")
        else:
            logger.info("Kết nối Model name thành công")

        self.model = AsyncOpenAI(
            api_key = self.api_key,
            base_url = self.base_url
           )
        self.Max_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "10000"))
        self.Max_INPUT_TOKENS = int(os.getenv("MAX_INPUT_TOKENS", "100000"))
        logger.info(f"Đã kết nối model thành công")

    async def test_call_api(self, prompt: str, max_output_tokens: Optional[int] = None, max_input_tokens: Optional[int] = None) -> str:
        max_output_tokens = max_output_tokens or self.Max_OUTPUT_TOKENS
        # DeepSeek's OpenAI-compatible Chat Completions API supports
        # `max_tokens` for output. It does not accept `max_input_tokens`.
        # Input limits are enforced by the model/context window instead.
        max_input_tokens = max_input_tokens or self.Max_INPUT_TOKENS
        try:
            response = await self.model.chat.completions.create(
                model = self.model_name,
                max_tokens = max_output_tokens,
                messages = [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                extra_body = {
                    "thinking":{
                        "type": "enabled"
                    }
                },
                reasoning_effort = "high"
            )
            content = response.choices[0].message.content
            logger.info("Model trả về kết quả thành công")
            return content
        except Exception as e:
            logger.error(f"Đã xảy ra lỗi khi gọi API: {e}")
            return "Đã xảy ra lỗi khi gọi API. Vui lòng thử lại sau."

        
