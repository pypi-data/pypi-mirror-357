
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-ntopng",
    version="0.1.0",
    description="An MCP Server for ntopng",
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
    install_requires=['mcp[cli]>=1.3.0', 'python-dotenv>=1.0.1', 'clickhouse-driver>=0.2.5', 'pip-system-certs>=4.0', 'requests>=2.32.3'],
    keywords=["mseep"] + ['ntop', 'mcp', 'llm', 'cybersecurity'],
)
