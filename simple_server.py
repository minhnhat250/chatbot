"""
=============================================================================
BẢN SERVER ĐƠN GIẢN NGUYÊN KHỐI (TẤT CẢ TRONG 1 FILE - ALL-IN-ONE)
=============================================================================
Nếu bạn muốn hiểu toàn bộ hoạt động của server Chatbot từ A đến Z
mà không muốn mở nhiều thư mục/file khác nhau, hãy đọc file này!

Cách chạy thử file này:
    python simple_server.py
Hoặc:
    uvicorn simple_server:app --reload

Các tính năng có sẵn trong file này:
1. Đọc API Key từ file .env (Gemini và DeepSeek).
2. Kết nối trực tiếp tới Google Gemini và DeepSeek.
3. Cung cấp API FastAPI cho Streamlit hoặc Web gọi vào:
   - GET  /         : Kiểm tra trạng thái server.
   - GET  /models   : Lấy danh sách model đang có API Key.
   - POST /chat     : Gửi câu hỏi cho AI và nhận câu trả lời.
   - POST /ask_ai   : Đường dẫn phụ tương thích với Streamlit.
=============================================================================
"""

import os
from typing import Annotated
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, StringConstraints
from google import genai
from openai import AsyncOpenAI

# =============================================================================
# 1. ĐỌC CẤU HÌNH TỪ FILE .env
# =============================================================================
# Hàm load_dotenv() sẽ tìm file .env trong thư mục và nạp các biến vào hệ thống
load_dotenv()

# Lấy các biến cấu hình ra để sử dụng
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL_NAME") or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")

# =============================================================================
# 2. KHỞI TẠO ỨNG DỤNG FASTAPI & CẤU HÌNH CORS
# =============================================================================
app = FastAPI(
    title="Chatbot AI Server (Đơn Giản)",
    description="Server API tích hợp chat Gemini & DeepSeek siêu gọn nhẹ.",
    version="1.0.0",
)

# Cho phép các ứng dụng giao diện (như Streamlit) kết nối tới server mà không bị chặn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# 3. ĐỊNH NGHĨA CẤU TRÚC DỮ LIỆU ĐẦU VÀO VÀ ĐẦU RA (PYDANTIC)
# =============================================================================
class ChatRequest(BaseModel):
    """Dữ liệu người dùng gửi lên server."""
    prompt: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] = Field(
        ..., description="Câu hỏi hoặc yêu cầu gửi đến AI"
    )
    model: str = Field(default="gemini", description="Chọn 'gemini' hoặc 'deepseek'")


class ChatResponse(BaseModel):
    """Dữ liệu server trả về cho người dùng."""
    answer: str = Field(description="Nội dung câu trả lời từ AI")
    provider: str = Field(description="Nhà cung cấp đã xử lý ('gemini' hoặc 'deepseek')")
    model: str = Field(description="Tên model cụ thể đã thực thi")


# =============================================================================
# 4. HÀM GỌI AI TRỰC TIẾP (GEMINI & DEEPSEEK)
# =============================================================================
async def ask_gemini(prompt: str) -> str:
    """Gửi câu hỏi tới Google Gemini và trả về câu trả lời."""
    if not GEMINI_API_KEY:
        raise ValueError("Chưa cấu hình GEMINI_API_KEY trong file .env!")

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = await client.aio.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    if not response.text:
        raise RuntimeError("Gemini trả về câu trả lời rỗng.")
    return response.text


async def ask_deepseek(prompt: str) -> str:
    """Gửi câu hỏi tới DeepSeek và trả về câu trả lời."""
    if not DEEPSEEK_API_KEY:
        raise ValueError("Chưa cấu hình DEEPSEEK_API trong file .env!")

    client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    response = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("DeepSeek trả về câu trả lời rỗng.")
    return content


# =============================================================================
# 5. CÁC ĐƯỜNG DẪN API (ENDPOINTS)
# =============================================================================
@app.get("/")
async def root():
    """Kiểm tra server còn sống hay không."""
    return {"status": "online", "message": "Server Chatbot đang hoạt động tốt!"}


@app.get("/models")
async def list_models():
    """Trả về danh sách AI và trạng thái xem đã nhập API Key chưa."""
    return {
        "models": [
            {
                "id": "gemini",
                "label": "Google Gemini",
                "model": GEMINI_MODEL,
                "available": bool(GEMINI_API_KEY),
            },
            {
                "id": "deepseek",
                "label": "DeepSeek",
                "model": DEEPSEEK_MODEL,
                "available": bool(DEEPSEEK_API_KEY),
            },
        ]
    }


@app.post("/chat", response_model=ChatResponse)
@app.post("/ask_ai", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint nhận câu hỏi và gọi đúng AI tương ứng.
    Áp dụng cho cả đường dẫn /chat và /ask_ai (để giao diện Streamlit hoạt động).
    """
    selected_model = request.model.lower().strip()

    try:
        # Nhánh 1: Nếu người dùng chọn Gemini
        if "gemini" in selected_model:
            answer = await ask_gemini(request.prompt)
            return ChatResponse(answer=answer, provider="gemini", model=GEMINI_MODEL)

        # Nhánh 2: Nếu người dùng chọn DeepSeek
        elif "deepseek" in selected_model:
            answer = await ask_deepseek(request.prompt)
            return ChatResponse(answer=answer, provider="deepseek", model=DEEPSEEK_MODEL)

        # Nhánh 3: Nếu gửi tên model không hỗ trợ
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mô hình '{request.model}' không được hỗ trợ. Hãy chọn 'gemini' hoặc 'deepseek'.",
            )

    except HTTPException:
        # Giữ nguyên các lỗi HTTP đã xác định (như 400, 422...)
        raise
    except ValueError as exc:
        # Lỗi thiếu API key hoặc cấu hình sai -> báo lỗi 400
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        # Lỗi không mong muốn khác khi kết nối với AI -> báo lỗi 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi gọi AI: {str(exc)}",
        )


# =============================================================================
# 6. KHỞI CHẠY SERVER KHI GỌI LỆNH TRỰC TIẾP: python simple_server.py
# =============================================================================
if __name__ == "__main__":
    uvicorn.run("simple_server:app", host="127.0.0.1", port=8000, reload=True)
