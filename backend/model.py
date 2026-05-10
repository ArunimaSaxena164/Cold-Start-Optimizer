
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

# # -------- LOAD DATA --------
# df = pd.read_csv("data/AzureLLMInferenceTrace_code.csv")

# df['timestamp'] = pd.to_datetime(df.iloc[:, 0])
# df = df.sort_values('timestamp')

# invocations = df.groupby(df['timestamp'].dt.floor('s')).size()

# data = invocations.values.astype(float)
# data = (data - np.mean(data)) / (np.std(data) + 1e-6)

import json

with open("stats.json", "r") as f:
    stats = json.load(f)

DATA_MEAN = stats["mean"]
DATA_STD = stats["std"]
DATA_THRESHOLD = stats["threshold"]
LAST_SEQUENCE = stats["last_sequence"]

# -------- MODEL (ALGO 1: PREDICTION) --------
class RNNModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.rnn = nn.RNN(1, 32, batch_first=True)
        self.fc = nn.Linear(32, 1)

    def forward(self, x):
        out, _ = self.rnn(x)
        return self.fc(out[:, -1, :])


# 🔥 LOAD PRETRAINED MODEL (IMPORTANT CHANGE)
model = RNNModel()
model.load_state_dict(torch.load("model.pth", map_location=torch.device("cpu")))
model.eval()


# -------- ALGO 2: PREWARMING --------
def compute_probability(pred, sigma):
    return 1 / (1 + np.exp(-pred))  # sigmoid

def prewarm_instances(p, required, capacity):
    max_prewarm_ratio = 0.8
    prewarm = int(np.ceil(p * required))
    return min(prewarm, int(max_prewarm_ratio * required), int(capacity))


# -------- ALGO 3: CAPACITY --------
def update_capacity(base_capacity, error):
    Kp, Ki, Kd = 0.1, 0.01, 0.05
    integral = error
    derivative = error
    return base_capacity + Kp*error + Ki*integral + Kd*derivative


# -------- ALGO 4: LOAD ADJUSTMENT --------
def adjust_load(pred, threshold, capacity):
    return int(np.ceil(pred * capacity)) if pred > threshold else 0

# def dynamic_threshold(values):
#     return np.mean(values) + np.std(values)


# -------- MAIN FUNCTION --------
def get_prediction(requests, machines):

    # Normalize input
    norm_req = (requests - DATA_MEAN) / (DATA_STD + 1e-6)

    seq = LAST_SEQUENCE + [norm_req]
    inp = torch.tensor(seq, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)

    pred = model(inp).detach().numpy().flatten()[0]

    sigma = DATA_STD

    # -------- REQUIRED --------
    required = int(np.ceil(requests / 100))

    # -------- BASE CAPACITY --------
    base_capacity = max(1, machines * 5)

    # -------- PREWARM --------
    p = compute_probability(pred, sigma)
    p = min(1.0, p * 3)

    prewarm = prewarm_instances(p, required, base_capacity)

    # -------- CAPACITY --------
    error = required - prewarm
    capacity = update_capacity(base_capacity, error)
    capacity = max(1, min(capacity, base_capacity))

    # -------- LOAD ADJUSTMENT --------
    threshold = DATA_THRESHOLD
    adjusted = adjust_load(pred, threshold, capacity)

    # -------- FINAL --------
    containers = min(required, int(capacity))
    cold_start = max(0, required - prewarm)

    return {
        "containers_needed": int(containers),
        "prediction": float(pred),
        "prewarm": int(prewarm),
        "adjusted": int(adjusted),
        "capacity": float(capacity),
        "required": int(required),
        "cold_start": int(cold_start)
    }