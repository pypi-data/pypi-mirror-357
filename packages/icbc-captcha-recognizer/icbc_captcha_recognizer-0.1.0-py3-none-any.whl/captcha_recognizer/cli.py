import os
import cv2
import torch
import json
from typing import Optional
from .models.litecnn import LiteCNN
from .utils.recognizer import Recognizer
from importlib.resources import files

def load_config() -> dict:
    """从打包资源中加载模型配置"""
    config_path = files('captcha_recognizer.config').joinpath('model_config.json')
    with config_path.open('r', encoding='utf-8') as f:
        return json.load(f)

def load_charset(charset_path: str) -> str:
    """读取字符集定义"""
    if not os.path.isfile(charset_path):
        raise FileNotFoundError(f"找不到字符集文件: {charset_path}")
    with open(charset_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def load_model(config: dict) -> torch.nn.Module:
    """加载预训练模型"""
    model_path = config.get('model_path')
    if not model_path:
        raise ValueError("配置中缺少 model_path")

    # 替换为打包后的绝对路径
    if not os.path.isabs(model_path):
        model_path = os.path.join(os.path.dirname(__file__), model_path)

    if os.path.isdir(model_path):
        model_path = os.path.join(model_path, 'model.pth')

    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"找不到模型文件: {model_path}")

    model = LiteCNN(
        config['image_height'],
        config['image_width'],
        config['num_classes'],
        config['max_text_length']
    )

    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    return model


def predict_file(path: str, verbose: bool = True) -> Optional[str]:
    """
    对单张图片或目录中的所有图片进行验证码识别

    参数:
        path: 图片路径或目录路径
        verbose: 是否打印识别结果（用于脚本/交互调试）

    返回:
        单图时返回识别字符串；目录时返回 None
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"输入路径不存在: {path}")

    config = load_config()

    # 读取 charset（允许路径为相对）
    charset_path = config.get('charset_path', '')
    if not os.path.isabs(charset_path):
        charset_path = os.path.join(os.path.dirname(__file__), charset_path)
    charset = load_charset(charset_path)

    model = load_model(config)
    recognizer = Recognizer(model, charset, config['image_height'], config['image_width'])

    def predict_image(image_path: str) -> Optional[str]:
        # 读取图像（灰度模式）
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            if verbose:
                print(f"[跳过] 无法读取图像: {image_path}")
            return None

        try:
            # 执行图像识别
            result = recognizer.predict(img)

            # --------------------- 调试代码 ---------------------
            # 提取文件名中的预期标签（假设标签是文件名的一部分，去掉扩展名）
            # filename = os.path.basename(image_path)
            # expected_label = os.path.splitext(filename)[0].split('_')[0]  # 假设标签在文件名开头

            # 检查识别结果与预期标签是否匹配
            # if result != expected_label:
            #     if verbose:
            #         print(f"[异常] {filename} 识别结果不匹配: 预期 {expected_label}, 实际 {result}")

            # 打印识别结果
            # if verbose:
            #     print(f"{filename} => {result}")
            # -----------------------------------------------------

            return result

        except Exception as e:
            if verbose:
                print(f"[错误] {filename} 识别失败: {e}")
            return None


    if os.path.isfile(path):
        return predict_image(path)

    elif os.path.isdir(path):
        image_files = sorted(
            f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        )
        for fname in image_files:
            predict_image(os.path.join(path, fname))
        return None

    else:
        raise ValueError(f"无效输入路径: {path}")


