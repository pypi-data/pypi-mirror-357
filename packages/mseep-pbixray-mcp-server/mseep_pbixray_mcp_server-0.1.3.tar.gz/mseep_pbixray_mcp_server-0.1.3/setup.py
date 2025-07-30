
from setuptools import setup, find_packages

setup(
    name="mseep-pbixray-mcp-server",
    version="0.1.3",
    description="An MCP server for analyzing Power BI files using PBIXRay",
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
    install_requires=['mcp>=1.2.0', 'pbixray>=0.1.0', 'numpy>=1.20.0', "pandas>=1.0.0; python_version >= '3.10'", "pandas>=1.0.0,<2.0.0; python_version < '3.10'"],
    keywords=["mseep"] + ['powerbi', 'pbix', 'analysis', 'mcp'],
)
