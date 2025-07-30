
from setuptools import setup, find_packages

setup(
    name="mseep-codemcp",
    version="0.7.1",
    description="MCP server for file operations",
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
    install_requires=['mcp[cli]>=1.2.0', 'ruff>=0.9.10', 'toml>=0.10.2', 'tomli>=2.1.1', 'anyio>=3.7.0', 'pyyaml>=6.0.0', 'editorconfig>=0.17.0', 'click>=8.1.8', 'agno>=1.2.16', 'anthropic>=0.49.0', 'fastapi>=0.115.12', 'uvicorn>=0.28.0', 'starlette>=0.35.1', 'google-genai>=1.10.0', 'pathspec>=0.12.1'],
    keywords=["mseep"] + [],
)
