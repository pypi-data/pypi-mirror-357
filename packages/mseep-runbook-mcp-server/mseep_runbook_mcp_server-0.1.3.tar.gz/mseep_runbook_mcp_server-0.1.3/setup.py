
from setuptools import setup, find_packages

setup(
    name="mseep-runbook-mcp-server",
    version="0.1.3",
    description="Runbook MCP server",
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
    install_requires=['httpx>=0.28.1', 'mcp[cli]>=1.6.0', 'pyyaml>=6.0.2', 'whoosh>=2.7.4'],
    keywords=["mseep"] + [],
)
