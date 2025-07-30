
from setuptools import setup, find_packages

setup(
    name="mseep-scrapegraph-mcp",
    version="1.0.3",
    description="MCP server for ScapeGraph API integration",
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
    install_requires=['mcp[cli]>=1.3.0', 'httpx>=0.24.0'],
    keywords=["mseep"] + [],
)
