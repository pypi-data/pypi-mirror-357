
from setuptools import setup, find_packages

setup(
    name="mseep-minimax-mcp",
    version="0.0.15",
    description="Minimax MCP Server",
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
    install_requires=['mcp[cli]>=1.6.0', 'fastapi>=0.109.2', 'uvicorn>=0.27.1', 'python-dotenv>=1.0.1', 'pydantic>=2.6.1', 'httpx>=0.28.1', 'fuzzywuzzy>=0.18.0', 'python-Levenshtein>=0.25.0', 'sounddevice>=0.5.1', 'soundfile>=0.13.1', 'requests>=2.31.0'],
    keywords=["mseep"] + ['minimax', 'mcp', 'text-to-speech', 'voice-cloning', 'video-generation'],
)
