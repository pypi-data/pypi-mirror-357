
from setuptools import setup, find_packages

setup(
    name="mseep-openfga-mcp",
    version="1.0.0",
    description="Model Context Protocol (MCP) server for OpenFGA",
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
    install_requires=['httpx>=0.28, <0.29', 'mcp>=1.4, <2', 'openfga-sdk>=0.9, <1', 'starlette>=0.27, <0.47', 'uvicorn>=0.23, <0.35'],
    keywords=["mseep"] + ['git', 'mcp', 'llm', 'automation'],
)
