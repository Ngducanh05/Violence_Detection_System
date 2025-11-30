import torch
import torch.nn as nn
import numpy as np


# ==========================
#  BI-LSTM CLASSIFIER MODEL
# ==========================
class ViolenceLSTM(nn.Module):
    def __init__(self, input_size=34, hidden_size=128, num_layers=2, num_classes=2):
        super(ViolenceLSTM, self).__init__()

        # LSTM 2-layer, bidirectional
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True
        )

        # Final FC: (hidden_size * 2) → 2 classes
        self.fc = nn.Linear(hidden_size * 2, num_classes)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]          # get last timestep
        out = self.fc(out)
        return out


# ==========================
#  CLASSIFY FUNCTION
# ==========================
def classify_pose(model, keypoints):
    """
    keypoints shape: (1, 17, 2)
    convert → flatten → feed to LSTM
    """
    arr = keypoints[0].detach().cpu().numpy().flatten().astype(np.float32)

    # reshape thành (batch=1, seq_len=1, features)
    tensor = torch.tensor(arr).unsqueeze(0).unsqueeze(0)

    with torch.no_grad():
        output = model(tensor)
        pred = torch.argmax(output, dim=1).item()

    return "violent" if pred == 1 else "non-violent"
