
from setuptools import setup, find_packages

setup(
    name="mseep-BigGo-MCP-Server",
    version="1.0.0",
    description="A Model Context Protocol (MCP) server that provides product search, price history tracking, and specification search capabilities.",
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
    install_requires=['aiohttp>=3.11.11', 'async-lru>=2.0.4', 'async-timeout>=5.0.1', 'elasticsearch8[async]>=8.17.1', 'mcp[cli]>=1.2.1', 'typing-extensions>=4.12.2'],
    keywords=["mseep"] + [],
)
