# LLM Gateway

FastAPI backend và giao diện chat Streamlit/Gradio hỗ trợ DeepSeek, Google Gemini.

## Cài đặt

```powershell
uv sync
Copy-Item .env.example .env
```

Điền API key của ít nhất một provider vào `.env`.

## Chạy ứng dụng

Mở terminal thứ nhất để chạy API:

```powershell
uv run uvicorn app.main:app --reload
```

Mở terminal thứ hai để chạy giao diện:

```powershell
uv run streamlit run streamlit_app.py
```

Hoặc chạy giao diện Gradio trong terminal riêng:

```powershell
uv run python gradio_app.py
```

Streamlit mở tại `http://localhost:8501`, Gradio tại `http://127.0.0.1:7860`.
Cả hai giao diện đều gọi FastAPI tại `http://127.0.0.1:8000`; có thể đổi địa chỉ
bằng biến môi trường `LLM_GATEWAY_URL`. Tài liệu API nằm tại `http://127.0.0.1:8000/docs`.

## API

- `GET /models`: danh sách provider, tên model cấu hình và trạng thái API key.
- `POST /ask_ai`: gửi `{ "prompt": "...", "model": "deepseek|gemini" }`.
