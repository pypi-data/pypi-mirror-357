
from setuptools import setup, find_packages

setup(
    name="mseep-geekbot-mcp",
    version="0.3.7",
    description="Model Context Protocol (MCP) server integrating Geekbot data and tools to Claude AI",
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
    install_requires=['aiohttp>=3.11.14', 'jinja2>=3.1.6', 'mcp[cli]>=1.5.0', 'python-dotenv>=1.1.0'],
    keywords=["mseep"] + ['geekbot', 'claude', 'ai', 'llm', 'mcp', 'api', 'integration', 'chatbot', 'anthropic'],
)
