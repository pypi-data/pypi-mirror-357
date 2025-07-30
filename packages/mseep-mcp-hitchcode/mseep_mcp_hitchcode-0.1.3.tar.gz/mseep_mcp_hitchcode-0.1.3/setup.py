
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-hitchcode",
    version="0.1.3",
    description="An MCP server providing tools for applying code templates and facilitating structured vibe coding assistance",
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
    install_requires=['anyio>=4.5', 'beautifulsoup4>=4.13.3', 'click>=8.1.0', 'httpx>=0.27', 'jinja2>=3.1.5', 'mcp', 'packaging>=24.2', 'pytest>=8.3.4', 'pyyaml>=6.0.2'],
    keywords=["mseep"] + ['mcp', 'llm', 'automation', 'web', 'fetch', 'code-templates', 'vibe-coding'],
)
