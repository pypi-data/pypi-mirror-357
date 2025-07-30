
from setuptools import setup, find_packages

setup(
    name="mseep-climatiq-mcp-server",
    version="0.2.3",
    description="Climatiq MCP server for carbon emission calculations",
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
    install_requires=['mcp[cli]>=1.4.1', 'httpx>=0.25.2', 'python-dotenv>=1.0.0', 'rich>=13.5.0', 'pydantic>=2.10.6'],
    keywords=["mseep"] + [],
)
