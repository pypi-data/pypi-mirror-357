
from setuptools import setup, find_packages

setup(
    name="mseep-attestable-mcp-server",
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
    install_requires=['anyio>=4.5', 'httpx>=0.27', 'httpx-sse>=0.4', 'pydantic>=2.7.2,<3.0.0', 'starlette>=0.27', 'sse-starlette>=1.6.1', 'pydantic-settings>=2.5.2', 'uvicorn>=0.23.1', 'docker>=7.1.0', 'jinja2>=3.1.6', 'tomli>=2.2.1', 'tomli-w>=1.2.0', 'pyyaml>=6.0.2', 'fastapi>=0.115.12'],
    keywords=["mseep"] + [],
)
