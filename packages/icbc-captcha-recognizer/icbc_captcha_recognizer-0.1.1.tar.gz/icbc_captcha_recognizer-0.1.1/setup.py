
from setuptools import setup, find_packages

setup(
    name="icbc-captcha-recognizer",
    version="0.1.1",
    description="ICBC CAPTCHA recognizer with pretrained model",
    author="lk",
    author_email="",
    packages=find_packages(include=["captcha_recognizer", "captcha_recognizer.*"]),
    package_data={
        "captcha_recognizer": [
            "config/*.json",
            "config/*.txt",
            "output/custom_captcha_model/model.pth",
        ]
    },
    include_package_data=True,
    install_requires=[
        'torch>=2.6.0',
        'torchvision>0.21.0',
        'opencv-python>4.6.0.66',
        'numpy>=1.26.4'
    ],
    entry_points={
        "console_scripts": [
            "captcha-predict=captcha_recognizer.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.10",
)
