
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-simple-tool",
    version="0.1.3",
    description="A simple MCP server exposing a website fetching tool",
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
    install_requires=['anyio>=4.5', 'click>=8.1.0', 'httpx>=0.27', 'mcp'],
    keywords=["mseep"] + ['mcp', 'llm', 'automation', 'web', 'fetch'],
)
