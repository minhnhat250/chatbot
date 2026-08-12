import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, StringConstraints

from models.deepseek import DeepSeekGateway
from models.gemini import GeminiGateway


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

MODEL_CONFIG = {
    "deepseek": {
        "label": "DeepSeek",
        "env_key": "DEEPSEEK_API",
        "model_env": "DEEPSEEK_MODEL",
        "default_model": "deepseek-v4-flash",
        "factory": DeepSeekGateway,
    },
    "gemini": {
        "label": "Google Gemini",
        "env_key": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL_NAME",
        "default_model": "gemini-3.5-flash",
        "factory": GeminiGateway,
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Khởi động ứng dụng")
    app.state.gateways = {}
    app.state.gateway_lock = asyncio.Lock()
    yield
    logger.info("Ứng dụng đã tắt")


app = FastAPI(
    title="LLM Gateway",
    description="API thống nhất để gọi nhiều nhà cung cấp mô hình ngôn ngữ.",
    version="1.2.0",
    lifespan=lifespan,
)


class AskRequest(BaseModel):
    prompt: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100_000)
    ]
    model: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class AskResponse(BaseModel):
    answer: str
    provider: str
    model: str


def get_model_catalog() -> list[dict[str, Any]]:
    def has_real_api_key(env_name: str) -> bool:
        value = os.getenv(env_name, "").strip()
        return bool(value and not value.lower().startswith("your_"))

    return [
        {
            "id": provider,
            "label": config["label"],
            "model": os.getenv(config["model_env"], config["default_model"]),
            "available": has_real_api_key(config["env_key"]),
        }
        for provider, config in MODEL_CONFIG.items()
    ]


async def get_gateway(request: Request, provider: str):
    gateway = request.app.state.gateways.get(provider)
    if gateway is not None:
        return gateway

    async with request.app.state.gateway_lock:
        gateway = request.app.state.gateways.get(provider)
        if gateway is None:
            gateway = MODEL_CONFIG[provider]["factory"]()
            request.app.state.gateways[provider] = gateway
    return gateway


@app.get("/")
async def root():
    return {"service": "LLM Gateway", "status": "ok", "docs": "/docs"}


@app.get("/models")
async def list_models():
    return {"models": get_model_catalog()}


@app.post("/ask_ai", response_model=AskResponse)
async def ask_ai(payload: AskRequest, request: Request):
    provider = payload.model.strip().lower()
    if provider not in MODEL_CONFIG:
        supported = ", ".join(MODEL_CONFIG)
        raise HTTPException(
            status_code=400,
            detail=f"Model không được hỗ trợ. Hãy chọn một trong: {supported}.",
        )

    try:
        gateway = await get_gateway(request, provider)
        answer = await gateway.generate(payload.prompt.strip())
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Không thể gọi provider %s", provider)
        raise HTTPException(
            status_code=502,
            detail=f"Không thể nhận phản hồi từ {MODEL_CONFIG[provider]['label']}.",
        ) from exc

    configured_model = os.getenv(
        MODEL_CONFIG[provider]["model_env"], MODEL_CONFIG[provider]["default_model"]
    )
    return AskResponse(answer=answer, provider=provider, model=configured_model)


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
