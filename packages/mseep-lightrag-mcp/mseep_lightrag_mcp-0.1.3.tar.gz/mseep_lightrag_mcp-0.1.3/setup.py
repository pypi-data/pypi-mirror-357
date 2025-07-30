
from setuptools import setup, find_packages

setup(
    name="mseep-lightrag_mcp",
    version="0.1.3",
    description="MCP Server for LightRAG",
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
    install_requires=['mcp>=1.2.0', 'httpx>=0.28.1', 'pydantic>=2.11', 'python-dotenv>=1.0.1', 'attrs>=25.3.0'],
    keywords=["mseep"] + [],
)
