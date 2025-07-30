
from setuptools import setup, find_packages

setup(
    name="mseep-fibery-mcp-server",
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
    install_requires=['click>=8.1.8', 'httpx>=0.28.1', 'mcp[cli]>=1.4.1', 'pydantic>=2.10.6', 'python-dotenv>=1.0.1'],
    keywords=["mseep"] + [],
)
