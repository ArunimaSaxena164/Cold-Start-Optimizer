# import numpy as np
# import pandas as pd
# import torch
# import torch.nn as nn

# # -------- LOAD DATA --------
# df = pd.read_csv("data/AzureLLMInferenceTrace_code.csv")

# df['timestamp'] = pd.to_datetime(df.iloc[:, 0])
# df = df.sort_values('timestamp')

# invocations = df.groupby(df['timestamp'].dt.floor('s')).size()

# data = invocations.values.astype(float)
# data = (data - np.mean(data)) / (np.std(data) + 1e-6)

# # -------- CREATE SEQUENCES --------
# def create_sequences(data, seq_length=10):
#     X, y = [], []
#     for i in range(len(data) - seq_length):
#         X.append(data[i:i+seq_length])
#         y.append(data[i+seq_length])
#     return np.array(X), np.array(y)

# X, y = create_sequences(data)

# # -------- MODEL (ALGO 1: PREDICTION) --------
# class RNNModel(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.rnn = nn.RNN(1, 32, batch_first=True)
#         self.fc = nn.Linear(32, 1)

#     def forward(self, x):
#         out, _ = self.rnn(x)
#         return self.fc(out[:, -1, :])

# model = RNNModel()

# X_train = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)
# y_train = torch.tensor(y, dtype=torch.float32)

# criterion = nn.MSELoss()
# optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# for epoch in range(10):
#     optimizer.zero_grad()
#     out = model(X_train)
#     loss = criterion(out.squeeze(), y_train)
#     loss.backward()
#     optimizer.step()

# # -------- ALGO 2: PREWARMING --------
# def compute_probability(pred, sigma):
#     return 1 / (1 + np.exp(-pred))  # sigmoid

# def prewarm_instances(p, required, capacity):
#     max_prewarm_ratio = 0.8

#     prewarm = int(np.ceil(p * required))

#     # 🔥 FINAL FIX: enforce BOTH limits
#     return min(prewarm, int(max_prewarm_ratio * required), int(capacity))

# # -------- ALGO 3: CAPACITY (PID CONTROL - STABLE) --------
# def update_capacity(base_capacity, error):
#     Kp, Ki, Kd = 0.1, 0.01, 0.05

#     integral = error
#     derivative = error

#     C_new = base_capacity + Kp*error + Ki*integral + Kd*derivative

#     return C_new

# # -------- ALGO 4: LOAD ADJUSTMENT --------
# def adjust_load(pred, threshold, capacity):
#     return int(np.ceil(pred * capacity)) if pred > threshold else 0

# def dynamic_threshold(values):
#     return np.mean(values) + np.std(values)

# # -------- MAIN FUNCTION --------
# def get_prediction(requests, machines):

#     # Normalize input
#     norm_req = (requests - np.mean(data)) / (np.std(data) + 1e-6)

#     seq = list(data[-9:]) + [norm_req]
#     inp = torch.tensor(seq, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)

#     pred = model(inp).detach().numpy().flatten()[0]

#     sigma = np.std(data)

#     # -------- REQUIRED --------
#     required = int(np.ceil(requests / 100))

#     # -------- BASE CAPACITY --------
#     base_capacity = max(1, machines * 5)

#     # -------- PREWARM --------
#     p = compute_probability(pred, sigma)

#     # scale probability (balanced tuning)
#     p = min(1.0, p * 3)

#     prewarm = prewarm_instances(p, required, base_capacity)

#     # -------- CAPACITY UPDATE --------
#     error = required - prewarm
#     capacity = update_capacity(base_capacity, error)

#     # clamp capacity
#     capacity = max(1, min(capacity, base_capacity))

#     # -------- LOAD ADJUSTMENT --------
#     threshold = dynamic_threshold(data)
#     adjusted = adjust_load(pred, threshold, capacity)

#     # -------- FINAL CONTAINERS --------
#     containers = min(required, int(capacity))

#     # -------- COLD START --------
#     cold_start = max(0, required - prewarm)

#     return {
#         "containers_needed": int(containers),
#         "prediction": float(pred),
#         "prewarm": int(prewarm),
#         "adjusted": int(adjusted),
#         "capacity": float(capacity),
#         "required": int(required),
#         "cold_start": int(cold_start)
#     }
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
data = (data - np.mean(data)) / (np.std(data) + 1e-6)

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

def dynamic_threshold(values):
    return np.mean(values) + np.std(values)


# -------- MAIN FUNCTION --------
def get_prediction(requests, machines):

    # Normalize input
    norm_req = (requests - np.mean(data)) / (np.std(data) + 1e-6)

    seq = list(data[-9:]) + [norm_req]
    inp = torch.tensor(seq, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)

    pred = model(inp).detach().numpy().flatten()[0]

    sigma = np.std(data)

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
    threshold = dynamic_threshold(data)
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