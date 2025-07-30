
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-naver",
    version="0.1.8",
    description="MCP server providing Naver Open APIs",
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
    install_requires=['fastmcp>=0.4.1', 'httpx>=0.28.1', 'pydantic>=2.10.6', 'xmltodict>=0.14.2'],
    keywords=["mseep"] + [],
)
