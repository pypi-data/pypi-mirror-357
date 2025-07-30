
from setuptools import setup, find_packages

setup(
    name="mseep-discord-raw-mcp",
    version="0.1.3",
    description="Discord Raw API MCP Server",
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
    install_requires=['discord.py>=2.3.2', 'mcp>=1.2.0', 'aiohttp>=3.9.1'],
    keywords=["mseep"] + [],
)
