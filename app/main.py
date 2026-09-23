"""
Điểm khởi chạy ứng dụng chính (FastAPI Server Main)
==================================================
File này là trung tâm của server:
1. Tạo ứng dụng FastAPI.
2. Cấu hình CORS để cho phép các ứng dụng giao diện (Streamlit, React, Vue...) có thể gọi tới.
3. Đăng ký các router xử lý nghiệp vụ (Chat AI).
4. Cung cấp các endpoint kiểm tra trạng thái (/ và /models).
"""

import sys
from pathlib import Path

# Đảm bảo Python luôn nhận diện được thư mục gốc của dự án (d:\MN)
# Giúp bạn có thể chạy trực tiếp lệnh: python app/main.py mà không bị lỗi ModuleNotFoundError
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers.chat import router as chat_router

# Khởi tạo ứng dụng FastAPI với tiêu đề và mô tả trực quan
app = FastAPI(
    title="Chatbot AI Gateway (Gemini & DeepSeek)",
    description="""
API Gateway tích hợp chat với **Google Gemini** và **DeepSeek**.
Bạn có thể thử nghiệm trực tiếp tại Swagger UI bằng cách:
1. Nhấn vào endpoint **/chat** hoặc **/ask_ai** bên dưới.
2. Nhấn nút **Try it out**.
3. Nhập câu hỏi vào `prompt` và chọn `model` là `"gemini"` hoặc `"deepseek"`.
4. Nhấn **Execute** để nhận kết quả từ AI.
""",
    version="1.0.0",
    docs_url="/docs",    # Địa chỉ xem tài liệu Swagger UI (http://127.0.0.1:8000/docs)
    redoc_url="/redoc",  # Địa chỉ xem tài liệu ReDoc
)

# Cấu hình CORS (Cross-Origin Resource Sharing)
# Giúp các website hoặc ứng dụng giao diện khác port/domain vẫn gửi request tới server được
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Cho phép mọi nguồn truy cập (có thể giới hạn khi deploy production)
    allow_credentials=True,    # Cho phép gửi cookie/token
    allow_methods=["*"],        # Cho phép mọi phương thức HTTP (GET, POST, PUT, DELETE...)
    allow_headers=["*"],        # Cho phép mọi tiêu đề header
)

# Đăng ký tập hợp các router xử lý chat vào ứng dụng chính
app.include_router(chat_router)


@app.get("/", tags=["Health"])
async def root():
    """
    Endpoint kiểm tra tình trạng hoạt động của server (Health Check).
    Bất kỳ ai truy cập vào trang chủ http://127.0.0.1:8000/ sẽ thấy thông tin này.
    """
    return {
        "service": "Chatbot AI Gateway",
        "status": "online",
        "docs": "/docs",
        "supported_models": ["gemini", "deepseek"],
    }


@app.get("/models", tags=["Health"])
async def list_models():
    """
    Endpoint cung cấp danh sách các mô hình AI đang hỗ trợ và trạng thái khả dụng.
    Ứng dụng Streamlit (streamlit_app.py) sẽ gọi endpoint này để hiển thị danh sách lựa chọn cho người dùng.
    """
    settings = get_settings()
    return {
        "models": [
            {
                "id": "gemini",
                "label": "Google Gemini",
                "model": settings.gemini_model_name,
                "available": bool(settings.gemini_api_key),  # True nếu đã điền API key trong .env
            },
            {
                "id": "deepseek",
                "label": "DeepSeek",
                "model": settings.effective_deepseek_model,
                "available": bool(settings.deepseek_api),   # True nếu đã điền API key trong .env
            },
        ]
    }


# Cho phép chạy file trực tiếp bằng lệnh `python app/main.py`
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
