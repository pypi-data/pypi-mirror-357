
from setuptools import setup, find_packages

setup(
    name="mseep-compiler-explorer-mcp",
    version="0.1.2",
    description="MCP server allowing LLMs to interact remotely with compilers",
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
    install_requires=['fastapi>=0.115.11', 'httpx>=0.28.1', 'mcp[cli]>=1.5.0', 'pydantic>=2.10.6', 'python-dotenv>=1.0.1', 'uvicorn>=0.34.0', 'websockets>=15.0.1'],
    keywords=["mseep"] + ['compiler', 'explorer', 'mcp', 'llm', 'claude'],
)
