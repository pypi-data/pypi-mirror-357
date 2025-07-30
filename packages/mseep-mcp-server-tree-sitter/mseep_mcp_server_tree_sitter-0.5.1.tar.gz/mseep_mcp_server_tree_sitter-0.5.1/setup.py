
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-tree-sitter",
    version="0.5.1",
    description="MCP Server for Tree-sitter code analysis",
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
    install_requires=['mcp[cli]>=0.12.0', 'tree-sitter>=0.20.0', 'tree-sitter-language-pack>=0.6.1', 'pyyaml>=6.0', 'pydantic>=2.0.0', 'types-pyyaml>=6.0.12.20241230'],
    keywords=["mseep"] + [],
)
