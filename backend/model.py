import numpy as np
import pandas as pd
import torch
import torch.nn as nn

# -------- LOAD DATA --------
df = pd.read_csv("data/AzureLLMInferenceTrace_code.csv")

df['timestamp'] = pd.to_datetime(df.iloc[:, 0])
df = df.sort_values('timestamp')

invocations = df.groupby(df['timestamp'].dt.floor('s')).size()

data = invocations.values.astype(float)
data = (data - np.mean(data)) / np.std(data)

# -------- SEQUENCES --------
def create_sequences(data, seq_length=10):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

X, y = create_sequences(data)

# -------- MODEL --------
class RNNModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.rnn = nn.RNN(1, 32, batch_first=True)
        self.fc = nn.Linear(32, 1)

    def forward(self, x):
        out, _ = self.rnn(x)
        return self.fc(out[:, -1, :])

model = RNNModel()

X_train = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)
y_train = torch.tensor(y, dtype=torch.float32)

criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(10):
    optimizer.zero_grad()
    out = model(X_train)
    loss = criterion(out.squeeze(), y_train)
    loss.backward()
    optimizer.step()

# -------- ALGO 1: Prediction --------
def predict():
    last_seq = X[-1]
    inp = torch.tensor(last_seq, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)
    return model(inp).detach().numpy().flatten()[0]

# -------- ALGO 2: Prewarming --------
def compute_probability(pred, sigma):
    return abs(pred) / (abs(pred) + sigma + 1e-6)

def prewarm(p, C):
    return int(np.ceil(p * C)) if p * C >= 0.5 else 0

# -------- ALGO 3: Capacity (PID) --------
integral = 0
prev_error = 0

def update_capacity(C, error):
    global integral, prev_error
    Kp, Ki, Kd = 0.1, 0.01, 0.05

    integral += error
    derivative = error - prev_error
    prev_error = error

    return C + Kp*error + Ki*integral + Kd*derivative

# -------- ALGO 4: Load Adjustment --------
def adjust(pred, threshold, C):
    return int(np.ceil(pred * C)) if pred > threshold else 0

# -------- MAIN --------
def get_prediction(requests, machines):
    norm_req = (requests - np.mean(data)) / (np.std(data) + 1e-6)

    seq = list(data[-9:]) + [norm_req]

    inp = torch.tensor(seq, dtype=torch.float32)\
            .unsqueeze(0).unsqueeze(-1)

    pred = model(inp).detach().numpy().flatten()[0]

    sigma = np.std(data)
    C = max(1, machines * 5)

    # probability
    p = abs(pred) / (abs(pred) + sigma + 1e-6)

    # prewarm
    prewarm = int(np.ceil(p * C)) if p * C >= 0.5 else 0

    # 🔥 NEW: estimate required containers from requests
    required = int(np.ceil(requests / 100))   # assumption: 1 container = 100 req

    # 🔥 FIXED cold start logic
    cold_start = max(0, required - prewarm)

    return {
        "containers_needed": prewarm,
        "prediction": float(pred),
        "prewarm": int(prewarm),
        "capacity": float(C),
        "required": int(required),
        "cold_start": int(cold_start)
    }