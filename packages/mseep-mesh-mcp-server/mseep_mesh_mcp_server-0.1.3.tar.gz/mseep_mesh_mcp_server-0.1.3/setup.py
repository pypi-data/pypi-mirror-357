
from setuptools import setup, find_packages

setup(
    name="mseep-mesh-mcp-server",
    version="0.1.3",
    description="MCP server for accessing mesh agents through Claude",
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
    install_requires=['anyio>=4.5', 'click>=8.1.0', 'httpx>=0.27', 'mcp', 'fastapi>=0.104.0', 'uvicorn>=0.24.0', 'pydantic>=2.0.0', 'aiohttp>=3.9.0', 'python-dotenv>=1.0.0', 'requests>=2.28.0', 'colorlog>=6.7.0'],
    keywords=["mseep"] + ['mcp', 'llm', 'automation', 'mesh', 'agents'],
)
