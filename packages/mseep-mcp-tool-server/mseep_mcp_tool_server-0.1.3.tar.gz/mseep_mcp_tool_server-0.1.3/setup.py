
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-tool-server",
    version="0.1.3",
    description="Add your description here",
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
    install_requires=['fal-client>=0.5.9', 'fastapi>=0.115.11', 'mcp[cli]>=1.3.0', 'python-dotenv>=1.0.1', 'sse-starlette>=2.2.1', 'uvicorn>=0.34.0'],
    keywords=["mseep"] + [],
)
