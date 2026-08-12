# LLM Gateway

FastAPI backend và giao diện chat Streamlit hỗ trợ DeepSeek, Google Gemini.

## Cài đặt

```powershell
uv sync
Copy-Item .env.example .env
```

Điền API key của ít nhất một provider vào `.env`.

## Chạy ứng dụng

Mở terminal thứ nhất để chạy API:

```powershell
uv run uvicorn app:app --reload
```

Mở terminal thứ hai để chạy giao diện:

```powershell
uv run streamlit run streamlit_app.py
```

Truy cập `http://localhost:8501`. Model được chọn trong thanh bên; UI chỉ hiển thị
những provider đã có API key. Tài liệu API nằm tại `http://127.0.0.1:8000/docs`.

## API

- `GET /models`: danh sách provider, tên model cấu hình và trạng thái API key.
- `POST /ask_ai`: gửi `{ "prompt": "...", "model": "deepseek|gemini" }`.
