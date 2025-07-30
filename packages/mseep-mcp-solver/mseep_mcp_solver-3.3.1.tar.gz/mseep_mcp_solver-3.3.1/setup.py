
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-solver",
    version="3.3.1",
    description="MCP server for Constraint, SAT, and SMT solving",
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
    install_requires=['mcp>=1.5.0', 'tomli>=2.2.1', 'six>=1.17.0', 'nest_asyncio>=1.6.0'],
    keywords=["mseep"] + [],
)
