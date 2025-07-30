
from setuptools import setup, find_packages

setup(
    name="mseep-xrpl-mcp-service",
    version="0.1.1",
    description="An MCP server implementation for interacting with the XRP Ledger blockchain",
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
    install_requires={'python': '^3.9', 'fastapi': '^0.104.0', 'uvicorn': '^0.24.0', 'xrpl-py': '^2.4.0', 'pydantic': '^2.4.2'},
    keywords=["mseep"] + [],
)
