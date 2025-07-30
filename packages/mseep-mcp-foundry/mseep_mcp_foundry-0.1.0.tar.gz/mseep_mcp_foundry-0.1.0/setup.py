
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-foundry",
    version="0.1.0",
    description="MCP Server for Azure AI Foundry (experimental)",
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
    install_requires=['mcp>=1.8.0', 'requests>=2.32.3', 'azure-mgmt-cognitiveservices>=13.0.0', 'azure-identity>=1.0', 'jinja2~=3.0', 'azure-search-documents>=11.5.2', 'azure-cli>=2.60.0', 'azure-ai-evaluation>=1.7.0', 'azure-ai-projects>=1.0.0b11'],
    keywords=["mseep"] + [],
)
