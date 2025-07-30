
from setuptools import setup, find_packages

setup(
    name="mseep-dappier-mcp",
    version="0.3.5",
    description="An MCP server for interacting with Dappier's RAG models",
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
    install_requires=['dappier>=0.3.3', 'mcp[cli]>=1.2.1', 'pydantic>=2.10.2'],
    keywords=["mseep"] + ['http', 'mcp', 'llm'],
)
