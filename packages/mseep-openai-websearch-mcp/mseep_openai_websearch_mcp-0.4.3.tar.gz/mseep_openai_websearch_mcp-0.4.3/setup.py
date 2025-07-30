
from setuptools import setup, find_packages

setup(
    name="mseep-openai-websearch-mcp",
    version="0.4.3",
    description="using openai websearch as mcp server",
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
    install_requires=['pydantic_extra_types==2.10.3', 'pydantic==2.10.6', 'mcp==1.3.0', 'tzdata==2025.1', 'openai==1.66.2', 'typer==0.15.2'],
    keywords=["mseep"] + [],
)
