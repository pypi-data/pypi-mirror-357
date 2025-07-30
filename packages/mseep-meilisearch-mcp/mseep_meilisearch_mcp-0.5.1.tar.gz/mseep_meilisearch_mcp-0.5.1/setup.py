
from setuptools import setup, find_packages

setup(
    name="mseep-meilisearch-mcp",
    version="0.5.1",
    description="MCP server for Meilisearch",
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
    install_requires=['meilisearch>=0.33.0', 'mcp>=0.1.0', 'httpx>=0.24.0', 'pydantic>=2.0.0'],
    keywords=["mseep"] + [],
)
