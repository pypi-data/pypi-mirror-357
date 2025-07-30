
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-filesystem",
    version="0.2.3",
    description="MCP server for filesystem search and manipulation with granular search, content search and file edits",
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
    install_requires=['fastmcp>=0.4.0', 'typer>=0.9.0', 'typing-extensions>=4.6.0'],
    keywords=["mseep"] + ['mcp', 'filesystem', 'claude', 'ai', 'fastmcp'],
)
