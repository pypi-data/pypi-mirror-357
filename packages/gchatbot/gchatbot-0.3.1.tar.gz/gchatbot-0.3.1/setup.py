from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gchatbot",
    version="0.3.1",
    author="João Matheus & Guilherme Fialho",
    author_email="guilhermec.fialho@gmail.com",
    description="A modern Python library for building Google Chat bots with serverless-safe async processing.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guilhermecf10/gchatbot",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.7",
    install_requires=[
        "google-auth>=2.0.0",
        "google-api-python-client>=2.0.0",
        "google-apps-chat>=0.1.0",
        "protobuf>=3.19.0"
    ],
    extras_require={
        "fastapi": [
            "fastapi>=0.70.0", 
            "uvicorn>=0.15.0"
        ],
        "async": [
            "aiohttp>=3.8.0",
            "asyncio-throttle>=1.0.0"
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=0.900"
        ],
        "all": [
            "fastapi>=0.70.0",
            "uvicorn>=0.15.0",
            "aiohttp>=3.8.0",
            "asyncio-throttle>=1.0.0"
        ]
    },
    keywords=[
        "google-chat", 
        "chatbot", 
        "bot", 
        "google-workspace", 
        "fastapi", 
        "async", 
        "serverless",
        "progressive-responses",
        "hybrid-sync-async"
    ],
    project_urls={
        "Bug Reports": "https://github.com/guilhermecf10/gchatbot/issues",
        "Source": "https://github.com/guilhermecf10/gchatbot",
        "Documentation": "https://github.com/guilhermecf10/gchatbot#readme",
    },
)
