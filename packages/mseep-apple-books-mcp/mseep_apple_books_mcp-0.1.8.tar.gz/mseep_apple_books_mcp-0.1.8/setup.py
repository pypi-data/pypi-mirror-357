
from setuptools import setup, find_packages

setup(
    name="mseep-apple-books-mcp",
    version="0.1.8",
    description="Model Context Protocol (MCP) server for Apple Books",
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
    install_requires=['click>=8.1.8', 'fastmcp>=0.4.1', 'py-apple-books>=1.3.0'],
    keywords=["mseep"] + ['apple-books', 'mcp', 'model-context-protocol', 'apple-books-mcp', 'llm', 'productivity'],
)
