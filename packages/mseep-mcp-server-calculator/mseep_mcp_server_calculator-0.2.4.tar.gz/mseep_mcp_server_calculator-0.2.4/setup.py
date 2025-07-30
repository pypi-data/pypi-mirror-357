
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-calculator",
    version="0.2.4",
    description="A Model Context Protocol server for calculating",
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
    install_requires=['mcp>=1.4.1'],
    keywords=["mseep"] + ['mcp', 'llm', 'math', 'calculator'],
)
