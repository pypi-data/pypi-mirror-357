
from setuptools import setup, find_packages

setup(
    name="mseep-elasticsearch-mcp-server",
    version="2.0.7",
    description="MCP Server for interacting with Elasticsearch and OpenSearch",
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
    install_requires=['elasticsearch==8.17.2', 'opensearch-py==2.8.0', 'mcp==1.9.2', 'python-dotenv==1.1.0', 'fastmcp==2.8.0', 'anthropic==0.49.0', 'tomli==2.2.1', 'tomli-w==1.2.0'],
    keywords=["mseep"] + [],
)
