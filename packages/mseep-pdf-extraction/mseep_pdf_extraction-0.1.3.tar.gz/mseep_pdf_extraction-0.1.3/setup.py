
from setuptools import setup, find_packages

setup(
    name="mseep-pdf-extraction",
    version="0.1.3",
    description="MCP server to extract contents from PDF files",
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
    install_requires=['mcp>=1.2.0', 'pypdf2>=3.0.1', 'pytesseract>=0.3.10', 'Pillow>=10.0.0', 'pydantic>=2.10.1,<3.0.0', 'pymupdf>=1.24.0'],
    keywords=["mseep"] + [],
)
