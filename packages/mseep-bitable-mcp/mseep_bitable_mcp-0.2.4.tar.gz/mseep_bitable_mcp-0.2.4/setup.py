
from setuptools import setup, find_packages

setup(
    name="mseep-bitable-mcp",
    version="0.2.4",
    description="This MCP server provides access to Lark bitable through the Model Context Protocol.",
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
    install_requires=['pybitable', 'mcp==1.3.0', 'typer'],
    keywords=["mseep"] + [],
)
