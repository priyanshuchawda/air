from setuptools import setup, find_packages

setup(
    name="airtouch",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'PyQt5',
        'mediapipe',
        'numpy',
        'pyautogui',
        'pynput'
    ]
) 