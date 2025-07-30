
from setuptools import setup, find_packages

setup(
    name="mseep-time-mcp-local",
    version="0.1.6",
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
    install_requires=['mcp>=1.3.0', 'pydantic>=2.10.6', 'tzdata>=2025.1', 'tzlocal>=5.3'],
    keywords=["mseep"] + [],
)
