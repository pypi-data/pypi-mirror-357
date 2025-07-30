
from setuptools import setup, find_packages

setup(
    name="mseep-pdf2md",
    version="0.1.3",
    description="PDF to Markdown MCP服务器",
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
    install_requires=['httpx>=0.28.1', 'mcp[cli]>=1.4.1', 'python-dotenv>=1.0.0', 'asyncio>=3.4.3', 'pathlib>=1.0.1', 'typer>=0.9.0'],
    keywords=["mseep"] + [],
)
