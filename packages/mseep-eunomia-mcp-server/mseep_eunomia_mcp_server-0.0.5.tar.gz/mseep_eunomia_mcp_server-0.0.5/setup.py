
from setuptools import setup, find_packages

setup(
    name="mseep-eunomia-mcp-server",
    version="0.0.5",
    description="",
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
    install_requires=['pip', 'uv', 'pydantic>=2.8.0', 'python-dotenv==1.0.0', 'pydantic-settings>=2.1.0', 'mcp>=1.1.2', 'eunomia-ai'],
    keywords=["mseep"] + [],
)
