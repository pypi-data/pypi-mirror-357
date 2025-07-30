
from setuptools import setup, find_packages

setup(
    name="mseep-vilnius-transport-mcp-server",
    version="0.1.3",
    description="This is Vilnius transport MCP server for claude desktop proof of concept",
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
    install_requires=['anthropic>=0.44.0', 'gtfs-kit>=10.1.1', 'httpx>=0.28.1', 'logging>=0.4.9.6', 'mcp>=1.2.0'],
    keywords=["mseep"] + [],
)
