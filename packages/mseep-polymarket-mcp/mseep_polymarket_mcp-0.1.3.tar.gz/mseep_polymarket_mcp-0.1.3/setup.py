
from setuptools import setup, find_packages

setup(
    name="mseep-polymarket_mcp",
    version="0.1.3",
    description="MCP Server for PolyMarket API",
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
    install_requires=['mcp>=0.1.0', 'httpx>=0.24.0', 'python-dotenv>=1.0.0', 'py-clob-client'],
    keywords=["mseep"] + [],
)
