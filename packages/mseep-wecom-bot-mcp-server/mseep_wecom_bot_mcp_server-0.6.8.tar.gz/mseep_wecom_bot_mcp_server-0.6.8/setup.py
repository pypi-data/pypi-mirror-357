
from setuptools import setup, find_packages

setup(
    name="mseep-wecom-bot-mcp-server",
    version="0.6.8",
    description="WeCom Bot MCP Server - A Python server for WeCom (WeChat Work) bot following the Model Context Protocol (MCP)",
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
    install_requires={'python': '>=3.10,<4.0', 'mcp': '>=1.3.0', 'notify-bridge': '>=0.3.0', 'platformdirs': '>=4.2.0', 'pydantic': '>=2.6.1', 'ftfy': '>=6.3.1', 'httpx': '>=0.28.1', 'pillow': '>=10.2.0', 'svglib': '>=1.5.1', 'tenacity': '>=9.0.0', 'loguru': '>=0.7.3', 'aiohttp': '>=3.11.13'},
    keywords=["mseep"] + [],
)
