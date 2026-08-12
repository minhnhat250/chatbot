import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st


st.set_page_config(page_title="LLM Gateway", page_icon="💬", layout="centered")


def api_get(url: str) -> dict:
    with urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def api_post(url: str, payload: dict) -> dict:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        try:
            message = json.loads(exc.read().decode("utf-8")).get("detail")
        except (json.JSONDecodeError, UnicodeDecodeError):
            message = None
        raise RuntimeError(message or f"API trả về lỗi HTTP {exc.code}.") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError("Không kết nối được API. Hãy kiểm tra FastAPI đang chạy.") from exc


if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💬 LLM Gateway")
st.caption("Chat với DeepSeek hoặc Google Gemini từ cùng một giao diện.")

with st.sidebar:
    st.header("Cấu hình")
    api_base_url = st.text_input(
        "Địa chỉ API",
        value=os.getenv("LLM_GATEWAY_URL", "http://127.0.0.1:8000"),
    ).rstrip("/")

    try:
        catalog = api_get(f"{api_base_url}/models")["models"]
        available_models = [item for item in catalog if item["available"]]
        if available_models:
            selected = st.selectbox(
                "Model",
                available_models,
                format_func=lambda item: f"{item['label']} · {item['model']}",
            )
        else:
            selected = None
            st.warning("Chưa có API key nào được cấu hình trong .env.")

        unavailable = [item["label"] for item in catalog if not item["available"]]
        if unavailable:
            st.caption("Chưa cấu hình: " + ", ".join(unavailable))
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        selected = None
        st.error("Không đọc được danh sách model từ FastAPI.")

    if st.button("Xóa cuộc trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("model"):
            st.caption(message["model"])

prompt = st.chat_input("Nhập câu hỏi...", disabled=selected is None)
if prompt and selected:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"Đang hỏi {selected['label']}..."):
            try:
                result = api_post(
                    f"{api_base_url}/ask_ai",
                    {"prompt": prompt, "model": selected["id"]},
                )
                answer = result["answer"]
                model_label = f"{selected['label']} · {result['model']}"
                st.markdown(answer)
                st.caption(model_label)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "model": model_label}
                )
            except (RuntimeError, KeyError) as exc:
                st.error(str(exc))
