
from setuptools import setup, find_packages

setup(
    name="mseep-ragflow-mcp",
    version="0.1.4",
    description="Simple MCP server for RAGFlow",
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
    install_requires=['mcp', 'uvicorn', 'starlette', 'ragflow-sdk', 'dotenv'],
    keywords=["mseep"] + [],
)
