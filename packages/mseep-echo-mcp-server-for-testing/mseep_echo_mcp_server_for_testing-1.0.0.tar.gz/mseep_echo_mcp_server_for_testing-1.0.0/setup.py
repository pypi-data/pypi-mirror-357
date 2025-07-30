
from setuptools import setup, find_packages

setup(
    name="mseep-echo-mcp-server-for-testing",
    version="1.0.0",
    description="A simple echo MCP (Model Context Protocol) Server for testing MCP Clients",
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
    install_requires=['ruff', 'mcp'],
    keywords=["mseep"] + ['mcp', 'server', 'testing'],
)
