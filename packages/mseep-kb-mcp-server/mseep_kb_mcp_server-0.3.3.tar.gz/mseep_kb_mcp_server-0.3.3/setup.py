
from setuptools import setup, find_packages

setup(
    name="mseep-kb-mcp-server",
    version="0.3.3",
    description="A Model Context Protocol (MCP) server implementation for txtai",
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
    install_requires=['mcp[cli]', 'trio', 'txtai[all,pipeline,graph]>=8.3.1', 'datasets', 'torch>=2.0.0', 'transformers==4.49.0', 'sentence-transformers>=2.2.0', 'httpx>=0.28.1', 'bitsandbytes==0.42.0', 'pydantic-settings>=2.0', 'networkx>=2.8.0', 'matplotlib>=3.5.0', 'PyPDF2>=2.0.0', 'python-docx>=0.8.11', 'beautifulsoup4>=4.10.0', 'pandas>=1.3.0', 'python-louvain>=0.16.0', 'markdown>=3.3.0', 'fast-langdetect>=0.3.1'],
    keywords=["mseep"] + [],
)
