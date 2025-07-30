
from setuptools import setup, find_packages

setup(
    name="mseep-AstrBot",
    version="3.5.18",
    description="易上手的多平台 LLM 聊天机器人及开发框架",
    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",
    author="mseep",
    author_email="support@skydeck.ai",
    maintainer="mseep",
    maintainer_email="support@skydeck.ai",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['aiocqhttp>=1.4.4', 'aiodocker>=0.24.0', 'aiohttp>=3.11.18', 'aiosqlite>=0.21.0', 'anthropic>=0.51.0', 'apscheduler>=3.11.0', 'beautifulsoup4>=4.13.4', 'certifi>=2025.4.26', 'chardet~=5.1.0', 'colorlog>=6.9.0', 'cryptography>=44.0.3', 'dashscope>=1.23.2', 'defusedxml>=0.7.1', 'dingtalk-stream>=0.22.1', 'docstring-parser>=0.16', 'faiss-cpu>=1.10.0', 'filelock>=3.18.0', 'google-genai>=1.14.0', 'googlesearch-python>=1.3.0', 'lark-oapi>=1.4.15', 'lxml-html-clean>=0.4.2', 'mcp>=1.8.0', 'nh3>=0.2.21', 'openai>=1.78.0', 'ormsgpack>=1.9.1', 'pillow>=11.2.1', 'pip>=25.1.1', 'psutil>=5.8.0', 'py-cord>=2.6.1', 'pydantic~=2.10.3', 'pydub>=0.25.1', 'pyjwt>=2.10.1', 'python-telegram-bot>=22.0', 'qq-botpy>=1.2.1', 'quart>=0.20.0', 'readability-lxml>=0.8.4.1', 'silk-python>=0.2.6', 'slack-sdk>=3.35.0', 'telegramify-markdown>=0.5.1', 'watchfiles>=1.0.5', 'websockets>=15.0.1', 'wechatpy>=1.8.18'],
    keywords=["mseep"] + [],
)
