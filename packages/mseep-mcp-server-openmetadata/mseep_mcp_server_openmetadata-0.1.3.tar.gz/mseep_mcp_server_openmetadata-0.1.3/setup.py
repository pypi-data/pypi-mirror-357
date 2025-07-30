
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-openmetadata",
    version="0.1.3",
    description="Model Context Protocol (MCP) server for OpenMetadata",
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
    install_requires=['httpx>=0.24.1', 'click>=8.1.7', 'mcp>=0.1.0', 'anyio>=4.2.0', 'starlette>=0.36.3', 'uvicorn>=0.27.1'],
    keywords=["mseep"] + ['mcp', 'openmetadata', 'metadata', 'model-context-protocol'],
)
