
from setuptools import setup, find_packages

setup(
    name="mseep-ebook-mcp",
    version="0.1.6",
    description="An MCP server for chatting with ebooks (PDF/EPUB).",
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
    install_requires=['ebooklib>=0.17.1', 'PyPDF2>=3.0.0', 'PyMuPDF>=1.20.0', 'beautifulsoup4>=4.12.0', 'html2text>=2020.1.16', 'pydantic>=2.8,<2.9', 'fastmcp>=2.1.2', 'typer>=0.9'],
    keywords=["mseep"] + [],
)
