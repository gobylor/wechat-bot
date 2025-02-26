from setuptools import setup, find_packages

setup(
    name="wechat-bot",
    version="0.1.0",
    description="A safe and stable WeChat bot for macOS using AppleScript",
    author="rl.yang",
    url="https://github.com/gobylor/wechat-bot",
    packages=find_packages(),
    install_requires=[
        "pyautogui>=0.9.54",
        "pyperclip>=1.8.2",
        "Pillow>=9.5.0",
        "opencv-python>=4.7.0",
        "numpy>=1.24.3",
        "pyobjc-core>=9.2; sys_platform == 'darwin'",
        "pyobjc-framework-Quartz>=9.2; sys_platform == 'darwin'",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Communications :: Chat",
    ],
)
