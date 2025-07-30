import os
import torch.nn as nn
import torch

class LiteCNN(nn.Module):
    def __init__(self, height, width, num_classes, max_length):
        super(LiteCNN, self).__init__()

        # CNN 特征提取部分
        self.conv = nn.Sequential(
            nn.Conv2d(1, 32, 3, 1, 1), nn.ReLU(), nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, 3, 1, 1), nn.ReLU(), nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, 3, 1, 1), nn.ReLU(), nn.MaxPool2d(2, 2),
        )
        conv_out_size = (height // 8) * (width // 8) * 128

        #  全连接输出
        self.fc = nn.Sequential(
            nn.Linear(conv_out_size, 512), nn.ReLU(),
            nn.Linear(512, max_length * num_classes)
        )
        self.max_length = max_length
        self.num_classes = num_classes

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        x = x.view(-1, self.max_length, self.num_classes)
        return x

    def load_model(self, path):
        self.load_state_dict(torch.load(os.path.join(path, 'model.pth'), map_location='cpu'))
        self.eval()

    def save_model(self, path):
        os.makedirs(path, exist_ok=True)
        torch.save(self.state_dict(), os.path.join(path, 'model.pth'))
