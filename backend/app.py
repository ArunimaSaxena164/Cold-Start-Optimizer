from fastapi import FastAPI
from pydantic import BaseModel
from model import get_prediction
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Input(BaseModel):
    requests: int
    machines: int

@app.post("/predict")
def predict_api(input: Input):
    return get_prediction(input.requests, input.machines)

