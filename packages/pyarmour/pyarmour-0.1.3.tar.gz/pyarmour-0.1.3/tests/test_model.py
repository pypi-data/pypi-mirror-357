import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output

# Create and save test model
model = SimpleCNN()
torch.save(model.state_dict(), "test_model.pth")

# Create test data
x_test = np.random.randn(10, 1, 28, 28).astype(np.float32)
y_test = np.random.randint(0, 10, size=(10,)).astype(np.int64)

# Save test data
np.savez("test_data.npz", x_test=x_test, y_test=y_test)
