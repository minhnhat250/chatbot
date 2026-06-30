import os
import logging
import uvicorn
from fastapi import FastAPI, Request,HTTPException
from pydantic import BaseModel
from models.deepseek import Deepseek

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

app = FastAPI()
deepseek = Deepseek()

class CheckPrompt(BaseModel):
    promt: str

