
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-simple-pubmed",
    version="0.1.14",
    description="An MCP server that provides access to PubMed articles through Entrez API.",
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
    install_requires=['mcp', 'biopython', 'metapub', 'httpx'],
    keywords=["mseep"] + [],
)
