
from setuptools import setup, find_packages

setup(
    name="mseep-codelogic-mcp-server",
    version="1.0.5",
    description="Integrates CodeLogic's powerful codebase knowledge graphs with a Model Context Protocol (MCP) server",
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
    install_requires=['debugpy>=1.8.12', 'httpx>=0.28.1', 'mcp[cli]>=1.3.0', 'pip-licenses>=5.0.0', 'python-dotenv>=1.0.1', 'tenacity>=9.0.0', 'toml>=0.10.2'],
    keywords=["mseep"] + ['codelogic', 'mcp', 'code-analysis', 'knowledge-graph', 'static-analysis'],
)
