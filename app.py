from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import logging
import uvicorn
from models.deepseek import Deepseek
from models.gemini import GeminiGateway
from contextlib import asynccontextmanager


logger = logging.getLogger(__name__)
logging.basicConfig(
    level= logging.INFO,
    format= "% (asctime)s - %(levelname)s -%(name)s - %(message)s"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Khởi động ứng dụng...")
    app.state.gateway = {
        "deepseek" : Deepseek(),
        "gemini" : GeminiGateway()
    }   
    yield
    logger.info("Ứng dụng đã tắt!")
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def run():
    return {"Hello": "World"}

class Request(BaseModel):
    prompt: str
    model: str

@app.post("/ask_ai")
async def ask_ai(req:Request):
    try:
        model_provider = req.model.lower()
        getway = app.state.gateway.get(model_provider)
        if not getway:
            raise HTTPException(status_code=400,detail="Không hỗ trợ model này")

        answer = await getway.test_call_api(req.prompt)
        return {"answer":answer}
    except HTTPException:
        raise HTTPException(status_code=500,detail="Đã có lỗi xảy ra")
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000,reload=True)
        



