
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-ynab",
    version="0.1.3",
    description="MCP server for YNAB API integration",
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
    install_requires=['mcp[cli]>=0.5.0', 'httpx>=0.26.0', 'pydantic>=2.0.0', 'ynab>=1.0.1', 'python-dotenv>=1.0.0', 'xdg>=6.0.0'],
    keywords=["mseep"] + [],
)
