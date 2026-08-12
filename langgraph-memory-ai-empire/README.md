# Bộ nhớ hội thoại với LangGraph — AI Empire Academy

Giáo trình thực hành bằng tiếng Việt, đi từ nguyên lý “LLM không tự nhớ” đến short-term
memory theo `thread_id`, quản lý context dài, running summary, long-term memory theo
`user_id`, persistence và tích hợp FastAPI/Streamlit.

## Cấu trúc

- `main.tex`, `sections/`: nguồn giáo trình LaTeX theo nhận diện AI Empire.
- `code/`: mã nguồn chạy được, test và ví dụ tích hợp.
- `build/main.pdf`: PDF sau khi build.

## Chuẩn bị code

```powershell
uv sync --extra dev
uv run pytest -q
```

Các ví dụ `01` đến `06` dùng model quyết định, không cần API key. File
`07_real_model_adapter.py` là adapter tham khảo cho DeepSeek/Gemini và chỉ chạy khi có
khóa tương ứng.

Tên thư mục `code/` trùng tên một module trong thư viện chuẩn Python, vì vậy các module bên trong
được chạy trực tiếp hoặc bằng tùy chọn `--app-dir code`; không import package dưới tên `code`.

## Build PDF

```powershell
.\build-latex.ps1
```

PDF đầu ra: `build/main.pdf`.
