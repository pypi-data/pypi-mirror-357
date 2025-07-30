
from setuptools import setup, find_packages

setup(
    name="mseep-grafana-loki-mcp",
    version="1.0.1",
    description="A FastMCP server for querying Loki logs from Grafana",
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
    install_requires=['fastmcp>=0.1.0', 'requests>=2.25.0'],
    keywords=["mseep"] + [],
)
