import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from lite_cnn import LiteCNN
from dataset_loader import CaptchaDataset
from torchvision import transforms

# --- 参数配置 ---
max_length = 4
charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
num_classes = len(charset)
height, width = 60, 160  # 请根据图片实际尺寸设置
batch_size = 64
epochs = 50
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- 加权 CrossEntropy ---
char_freq = [3, 812, 1260, 1245, 682, 1193, 1260, 1179, 753, 717, 740, 502, 474, 474, 450, 485, 483, 502, 446, 461, 468, 476, 510, 475, 476, 442, 489, 522, 469]
char_weights = torch.tensor([1/f for f in char_freq])
char_weights = char_weights / char_weights.sum() * len(char_freq)
criterion = nn.CrossEntropyLoss(weight=char_weights.to(device))

# --- 模型 & 优化器 ---
model = LiteCNN(height, width, num_classes, max_length).to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-3)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.9)

# --- 数据增强 ---
train_transform = transforms.Compose([
    transforms.RandomRotation(10),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), shear=5),
    transforms.ToTensor()
])
val_transform = transforms.ToTensor()

train_set = CaptchaDataset("dataset/train", charset, train_transform)
val_set = CaptchaDataset("dataset/val", charset, val_transform)

train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=2)
val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=False, num_workers=2)

# --- 评估函数 ---
def evaluate(model, loader):
    model.eval()
    correct_all = 0
    correct_per_char = 0
    total = 0

    with torch.no_grad():
        for imgs, labels in loader:
            imgs = imgs.to(device)
            labels = labels.to(device)
            outputs = model(imgs)
            pred = outputs.argmax(dim=2)

            correct_all += ((pred == labels).all(dim=1)).sum().item()
            correct_per_char += (pred == labels).sum().item()
            total += labels.numel()

    return correct_all / len(loader.dataset), correct_per_char / total

# --- 训练过程 ---
best_acc = 0
for epoch in range(epochs):
    model.train()
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)

        outputs = model(imgs)  # [B, 4, 62]
        loss = sum(criterion(outputs[:, i, :], labels[:, i]) for i in range(max_length)) / max_length

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    acc_all, acc_char = evaluate(model, val_loader)
    scheduler.step()

    print(f"Epoch {epoch+1} | Loss: {loss.item():.4f} | Full Acc: {acc_all:.4f} | Char Acc: {acc_char:.4f}")

    if acc_all > best_acc:
        best_acc = acc_all
        torch.save(model.state_dict(), "best_model.pth")
        print("✅ Best model updated.")
