
from setuptools import setup, find_packages

setup(
    name="mseep-elasticsearch7-mcp-server",
    version="1.0.3",
    description="MCP Server for interacting with Elasticsearch 7.x",
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
    install_requires=['elasticsearch>=7.0.0,<8.0.0', 'mcp>=1.0.0', 'python-dotenv>=1.0.0', 'fastmcp>=0.4.0'],
    keywords=["mseep"] + [],
)
