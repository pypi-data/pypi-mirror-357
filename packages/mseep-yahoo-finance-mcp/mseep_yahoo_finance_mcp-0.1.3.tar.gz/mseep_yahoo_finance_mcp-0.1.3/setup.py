
from setuptools import setup, find_packages

setup(
    name="mseep-yahoo-finance-mcp",
    version="0.1.3",
    description="MCP server implementation for yahoo finance integration",
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
    install_requires=['mcp[cli]>=1.6.0', 'yfinance>=0.2.62'],
    keywords=["mseep"] + [],
)
