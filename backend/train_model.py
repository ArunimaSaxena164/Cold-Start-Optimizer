import numpy as np
import pandas as pd
import torch
import torch.nn as nn

# Load data
df = pd.read_csv("data/AzureLLMInferenceTrace_code.csv")

df['timestamp'] = pd.to_datetime(df.iloc[:, 0])
df = df.sort_values('timestamp')

invocations = df.groupby(df['timestamp'].dt.floor('s')).size()

data = invocations.values.astype(float)
data = (data - np.mean(data)) / (np.std(data) + 1e-6)

# Create sequences
def create_sequences(data, seq_length=10):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

X, y = create_sequences(data)

# Model
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

# Train
for epoch in range(10):
    optimizer.zero_grad()
    out = model(X_train)
    loss = criterion(out.squeeze(), y_train)
    loss.backward()
    optimizer.step()

    if epoch % 2 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item()}")

# Save model
torch.save(model.state_dict(), "model.pth")

print("Model saved as model.pth")