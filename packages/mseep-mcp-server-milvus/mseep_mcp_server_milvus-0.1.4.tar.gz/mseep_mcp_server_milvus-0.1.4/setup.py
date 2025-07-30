
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-milvus",
    version="0.1.4",
    description="MCP server for Milvus",
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
    install_requires=['fastmcp>=2.6.1', 'pymilvus>=2.5.1', 'click>=8.0.0', 'ruff>=0.11.0', 'python-dotenv>=1.0.0'],
    keywords=["mseep"] + [],
)
