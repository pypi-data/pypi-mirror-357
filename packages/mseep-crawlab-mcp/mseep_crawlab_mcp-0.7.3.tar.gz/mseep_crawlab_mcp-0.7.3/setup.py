
from setuptools import setup, find_packages

setup(
    name="mseep-crawlab-mcp",
    version="0.7.3",
    description="Crawlab Model Control Protocol (MCP) - A framework for AI agents",
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
    install_requires=['fastapi>=0.95.0', 'uvicorn>=0.21.1', 'aiohttp>=3.8.4', 'python-dotenv>=1.0.0'],
    keywords=["mseep"] + [],
)
