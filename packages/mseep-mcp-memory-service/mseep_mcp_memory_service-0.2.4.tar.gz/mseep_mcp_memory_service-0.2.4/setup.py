
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-memory-service",
    version="0.2.4",
    description="A semantic memory service using ChromaDB and sentence-transformers",
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
    install_requires=['chromadb==0.5.23', 'sentence-transformers', 'tokenizers==0.20.3', 'mcp>=1.0.0,<2.0.0'],
    keywords=["mseep"] + [],
)
