# Dùng json để mã hóa dữ liệu gửi đi và giải mã phản hồi JSON từ FastAPI.
import json
# Dùng os để đọc địa chỉ FastAPI từ biến môi trường của máy.
import os
# Dùng HTTPError để xử lý riêng các phản hồi HTTP có mã lỗi như 400 hoặc 500.
from urllib.error import HTTPError
# Dùng URLError để nhận biết trường hợp không kết nối được tới API.
from urllib.error import URLError
# Dùng Request để tạo yêu cầu HTTP POST có JSON trong phần thân.
from urllib.request import Request
# Dùng urlopen để gửi yêu cầu HTTP mà không cần cài thêm thư viện mạng.
from urllib.request import urlopen

# Nạp Gradio để dựng giao diện web từ hàm Python.
import gradio as gr


# Lấy địa chỉ API từ biến môi trường; nếu chưa đặt thì dùng FastAPI local cổng 8000.
API_URL = os.getenv("LLM_GATEWAY_URL", "http://127.0.0.1:8000").rstrip("/")


# Khai báo hàm mà Gradio gọi khi người dùng gửi câu hỏi và chọn model.
def ask_ai(prompt: str, model: str) -> str:
    # Ghi chú ngắn về trách nhiệm của hàm để người đọc tra cứu ngay tại mã nguồn.
    """Gửi một câu hỏi đến endpoint chat hiện có của FastAPI và trả về nội dung hiển thị."""
    # Chặn nội dung rỗng ngay trên giao diện để người dùng nhận thông báo dễ hiểu.
    if not prompt.strip():
        # Trả thông báo này vào ô kết quả và không gửi yêu cầu rỗng đến API.
        return "Vui lòng nhập câu hỏi."

    # Tạo yêu cầu HTTP POST đến endpoint chat của pipeline FastAPI.
    request = Request(
        f"{API_URL}/chat",  # Nối địa chỉ API với đúng đường dẫn xử lý hội thoại.
        data=json.dumps({"prompt": prompt, "model": model}).encode("utf-8"),  # Đóng gói câu hỏi và model thành JSON dạng byte.
        headers={"Content-Type": "application/json"},  # Báo cho FastAPI biết phần thân yêu cầu là JSON.
        method="POST",  # Dùng POST vì yêu cầu có gửi dữ liệu câu hỏi lên server.
    )

    # Bắt đầu gửi yêu cầu và xử lý riêng các loại lỗi thường gặp ở giao tiếp API.
    try:
        # Chờ phản hồi tối đa 180 giây vì model AI có thể xử lý câu hỏi lâu.
        with urlopen(request, timeout=300) as response:
            # Đọc byte từ phản hồi, giải mã UTF-8 rồi chuyển JSON thành dictionary Python.
            result = json.loads(response.read().decode("utf-8"))
    # Bắt phản hồi HTTP có mã lỗi do FastAPI hoặc provider trả về.
    except HTTPError as exc:
        # Thử đọc phần mô tả lỗi JSON do API gửi trong phần thân phản hồi.
        try:
            # Lấy trường detail để người dùng biết vì sao yêu cầu không thành công.
            detail = json.loads(exc.read().decode("utf-8")).get("detail")
        # Nếu phần lỗi không phải JSON hợp lệ hoặc không phải UTF-8 thì dùng thông báo dự phòng.
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Đặt detail rỗng để dòng trả kết quả dùng nội dung dự phòng bên dưới.
            detail = None
        # Trả mã HTTP và nội dung lỗi trong ô kết quả của giao diện.
        return f"Lỗi API (HTTP {exc.code}): {detail or 'Không xử lý được yêu cầu.'}"
    # Bắt lỗi mạng hoặc hết thời gian chờ khi không liên lạc được với FastAPI.
    except (URLError, TimeoutError):
        # Hướng dẫn người dùng kiểm tra backend thay vì hiện traceback kỹ thuật.
        return "Không kết nối được FastAPI. Hãy kiểm tra server đang chạy."

    # Ghép câu trả lời với provider và model để người dùng biết model nào đã xử lý.
    return f"{result['answer']}\n\n{result['provider']} · {result['model']}"


# Tạo giao diện một màn hình gồm ô câu hỏi, danh sách model và ô câu trả lời.
demo = gr.Interface(
    fn=ask_ai,  # Dùng hàm ask_ai làm xử lý cho nút gửi của giao diện.
    inputs=[  # Khai báo các giá trị Gradio chuyển vào hàm theo thứ tự.
        gr.Textbox(label="Câu hỏi", lines=4, placeholder="Nhập câu hỏi của bạn..."),  # Ô nhập câu hỏi nhiều dòng.
        gr.Dropdown(  # Tạo danh sách chọn một trong hai provider mà pipeline hỗ trợ.
            choices=[("Google Gemini", "gemini"), ("DeepSeek", "deepseek")],  # Hiện nhãn dễ đọc nhưng gửi mã provider cho API.
            value="gemini",  # Chọn Gemini mặc định khi mở trang.
            label="Model",  # Đặt tên hiển thị cho danh sách model.
        ),  # Kết thúc cấu hình danh sách chọn model.
    ],  # Kết thúc danh sách các trường đầu vào.
    outputs=gr.Textbox(label="Trả lời", lines=8),  # Hiện câu trả lời và thông tin model trong ô nhiều dòng.
    title="LLM Gateway",  # Đặt tiêu đề hiển thị ở đầu trang Gradio.
)  # Kết thúc cấu hình giao diện Gradio.


# Chỉ khởi chạy web server khi chạy trực tiếp file này, không chạy lúc file được import để test.
if __name__ == "__main__":
    # Mở giao diện tại localhost; URL cụ thể được Gradio in ra terminal.
    demo.launch()
