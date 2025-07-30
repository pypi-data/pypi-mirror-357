
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-unitycatalog",
    version="0.1.3",
    description="A Model Context Protocol server that enables LLM agents to execute Unity Catalog functions seamlessly.",
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
    install_requires=['mcp>=1.2.1', 'pydantic>=2.10.6', 'pydantic-settings>=2.7.1', 'unitycatalog-ai>=0.1.0'],
    keywords=["mseep"] + ['unitycatalog', 'mcp', 'llm', 'automation'],
)
