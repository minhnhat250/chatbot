"""
File khởi động Server nhanh (Server Entrypoint)
==============================================
Đây là file chạy chính ở thư mục gốc của dự án.
Để khởi động server FastAPI, bạn chỉ cần mở terminal và chạy lệnh:
    python app.py
Server sẽ khởi chạy tại: http://127.0.0.1:8000
Tài liệu tương tác Swagger UI: http://127.0.0.1:8000/docs
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    # Khởi động web server Uvicorn
    # - "app.main:app": Nạp biến `app` từ file `app/main.py`
    # - host="127.0.0.1": Chỉ lắng nghe trên máy cục bộ (localhost)
    # - port=8000: Cổng kết nối
    # - reload=True: Tự động tải lại server khi bạn lưu file code mới (rất tiện khi lập trình)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
