
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-chat-analysis",
    version="0.1.3",
    description="MCP server for chat analysis using vector embeddings and knowledge graphs",
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
    install_requires=['modelcontextprotocol>=0.1.0', 'qdrant-client>=1.7.0', 'neo4j>=5.15.0', 'sentence-transformers>=2.2.2', 'pydantic>=2.5.0', 'python-dotenv>=1.0.0'],
    keywords=["mseep"] + ['mcp', 'chat', 'analysis', 'vector', 'knowledge-graph'],
)
