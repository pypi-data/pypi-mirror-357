from setuptools import setup, find_packages

setup(
    name="opal_tools_sdk",
    version="0.1.2.dev0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "pydantic>=2.0.0",
        "httpx>=0.24.1",
        "deprecated>=1.2.18",
    ],
    author="Optimizely",
    author_email="opal-team@optimizely.com",
    description="SDK for creating Opal-compatible tools services",
    keywords="opal, tools, sdk, ai, llm",
    url="https://github.com/optimizely/opal-tools-sdk",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.10",
)