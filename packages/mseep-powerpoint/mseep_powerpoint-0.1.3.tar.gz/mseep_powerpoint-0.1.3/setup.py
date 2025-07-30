
from setuptools import setup, find_packages

setup(
    name="mseep-powerpoint",
    version="0.1.3",
    description="A MCP server project that creates powerpoint presentations",
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
    install_requires=['mcp>=1.3.0', 'pillow>=11.1.0', 'python-pptx>=1.0.2', 'requests>=2.32.3', 'together>=1.4.1'],
    keywords=["mseep"] + [],
)
