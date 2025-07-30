import torch
import cv2

class Recognizer:
    def __init__(self, model, charset, height, width):
        self.model = model
        self.charset = charset
        self.height = height
        self.width = width

    def predict(self, img):
        img = cv2.resize(img, (self.width, self.height))
        img = img.astype('float32') / 255.0
        img = torch.tensor(img).unsqueeze(0).unsqueeze(0)
        with torch.no_grad():
            output = self.model(img)
        pred = torch.argmax(output, dim=2)[0]
        return ''.join([self.charset[i] for i in pred])
