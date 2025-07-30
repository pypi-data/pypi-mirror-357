
from setuptools import setup, find_packages

setup(
    name="mseep-ramp-mcp",
    version="0.0.4",
    description="Ramp MCP Demo",
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
    install_requires=['httpx>=0.28.1', 'mcp[cli]>=1.3.0', 'uuid>=1.30.0', 'iso4217>=1.12.20240625', 'flatten-json>=0.1.14'],
    keywords=["mseep"] + [],
)
