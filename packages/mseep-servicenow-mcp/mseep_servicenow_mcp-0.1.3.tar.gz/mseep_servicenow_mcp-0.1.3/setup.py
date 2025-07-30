
from setuptools import setup, find_packages

setup(
    name="mseep-servicenow-mcp",
    version="0.1.3",
    description="A Model Context Protocol (MCP) server implementation for ServiceNow",
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
    install_requires=['mcp[cli]==1.3.0', 'requests>=2.28.0', 'pydantic>=2.0.0', 'python-dotenv>=1.0.0', 'starlette>=0.27.0', 'uvicorn>=0.22.0', 'httpx>=0.24.0', 'PyYAML>=6.0'],
    keywords=["mseep"] + [],
)
