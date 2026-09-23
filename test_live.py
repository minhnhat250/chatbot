"""
Script kiểm tra thực tế (Live Test)
==================================
Chạy file này bằng lệnh:
    .venv\Scripts\python.exe test_live.py
Script sẽ gửi câu hỏi thực tế đến cả Google Gemini và DeepSeek để kiểm tra.
"""

import sys
import io
import asyncio
from fastapi.testclient import TestClient

# Thiết lập mã hóa UTF-8 cho console Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=" * 60)
print("BẮT ĐẦU KIỂM TRA SERVER FASTAPI VÀ CÁC AI PROVIDER")
print("=" * 60)

from app.main import app

client = TestClient(app)

# 1. Test Endpoint /
print("\n[1] Kiểm tra Endpoint GET / (Health Check):")
res_root = client.get("/")
print("Status Code:", res_root.status_code)
print("Response:", res_root.json())

# 2. Test Endpoint /models
print("\n[2] Kiểm tra Endpoint GET /models (Danh sách AI):")
res_models = client.get("/models")
print("Status Code:", res_models.status_code)
for m in res_models.json().get("models", []):
    status_str = "Sẵn sàng (Đã có API Key)" if m['available'] else "Chưa có key"
    print(f" - {m['label']} (id='{m['id']}', model='{m['model']}'): {status_str}")

# 3. Test Endpoint /chat với Google Gemini (Live API Call)
print("\n[3] Kiểm tra Endpoint POST /chat với Google Gemini:")
payload_gemini = {
    "prompt": "Xin chào! Hãy giới thiệu bạn là ai trong đúng 1 câu ngắn gọn.",
    "model": "gemini"
}
try:
    res_gemini = client.post("/chat", json=payload_gemini)
    print("Status Code:", res_gemini.status_code)
    if res_gemini.status_code == 200:
        data = res_gemini.json()
        print("Model thực thi:", data.get("model"))
        print("Provider:", data.get("provider"))
        print("Câu trả lời từ Gemini:\n>>>", data.get("answer"))
    else:
        print("Lỗi từ Gemini:", res_gemini.json())
except Exception as e:
    print("Ngoại lệ khi gọi Gemini:", e)

# 4. Test Endpoint /chat với DeepSeek
print("\n[4] Kiểm tra Endpoint POST /chat với DeepSeek:")
payload_deepseek = {
    "prompt": "Chào bạn! 1 + 1 bằng mấy? Trả lời ngắn gọn.",
    "model": "deepseek"
}
try:
    res_deepseek = client.post("/chat", json=payload_deepseek)
    print("Status Code:", res_deepseek.status_code)
    if res_deepseek.status_code == 200:
        data = res_deepseek.json()
        print("Model thực thi:", data.get("model"))
        print("Provider:", data.get("provider"))
        print("Câu trả lời từ DeepSeek:\n>>>", data.get("answer"))
    else:
        print("Lỗi/Phản hồi từ DeepSeek:", res_deepseek.json())
except Exception as e:
    print("Ngoại lệ khi gọi DeepSeek:", e)

print("\n" + "=" * 60)
print("HOÀN TẤT KIỂM TRA!")
print("=" * 60)
