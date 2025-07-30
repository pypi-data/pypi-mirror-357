
from setuptools import setup, find_packages

setup(
    name="mseep-things3-enhanced-mcp",
    version="1.0.0",
    description="Enhanced FastMCP server for Things 3 app integration with Claude Desktop and Windsurf - featuring reliability improvements, caching, and AppleScript bridge",
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
    install_requires=['httpx>=0.28.1', 'mcp[cli]>=1.2.0', 'things-py>=0.0.15'],
    keywords=["mseep"] + ['mcp', 'anthropic', 'claude', 'things3', 'things', 'task-management', 'productivity', 'fastmcp', 'macos', 'apple'],
)
