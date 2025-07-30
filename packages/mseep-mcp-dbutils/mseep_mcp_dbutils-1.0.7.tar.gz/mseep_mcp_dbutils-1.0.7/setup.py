
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-dbutils",
    version="1.0.7",
    description="MCP Database Utilities Service",
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
    install_requires=['mcp>=1.7.1', 'typer>=0.9.0', 'psycopg2-binary>=2.9.10', 'python-dotenv>=1.0.1', 'pyyaml>=6.0.2', 'mysql-connector-python>=8.2.0'],
    keywords=["mseep"] + [],
)
