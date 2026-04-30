from fastapi import FastAPI
from pydantic import BaseModel
from model import get_prediction, data
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

@app.get("/dataset")
def dataset():
    return {
        "data": data[:200].tolist()   # make sure key = "data"
    }