
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-text-editor",
    version="1.0.0",
    description="MCP Text Editor Server - Edit text files via MCP protocol",
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
    install_requires=['asyncio>=3.4.3', 'mcp>=1.1.2', 'chardet>=5.2.0'],
    keywords=["mseep"] + [],
)
