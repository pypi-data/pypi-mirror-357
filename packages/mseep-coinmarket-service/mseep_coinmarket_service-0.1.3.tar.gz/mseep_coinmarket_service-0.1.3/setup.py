
from setuptools import setup, find_packages

setup(
    name="mseep-coinmarket-service",
    version="0.1.3",
    description="Coinmarket MCP Server",
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
    install_requires=['mcp>=1.0.0', 'python-dotenv>=1.0.1', 'requests>=2.32.3', 'ruff>=0.8.1'],
    keywords=["mseep"] + [],
)
