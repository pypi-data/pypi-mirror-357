
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-atlassian",
    version="1.0.1",
    description="The Model Context Protocol (MCP) Atlassian integration is an open-source implementation that bridges Atlassian products (Jira and Confluence) with AI language models following Anthropic's MCP specification. This project enables secure, contextual AI interactions with Atlassian tools while maintaining data privacy and security. Key features include:",
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
    install_requires=['atlassian-python-api>=4.0.0', 'requests[socks]>=2.31.0', 'beautifulsoup4>=4.12.3', 'httpx>=0.28.0', 'mcp>=1.8.0,<2.0.0', 'fastmcp>=2.3.4,<2.4.0', 'python-dotenv>=1.0.1', 'markdownify>=0.11.6', 'markdown>=3.7.0', 'markdown-to-confluence>=0.3.0,<0.4.0', 'pydantic>=2.10.6', 'trio>=0.29.0', 'click>=8.1.7', 'uvicorn>=0.27.1', 'starlette>=0.37.1', 'thefuzz>=0.22.1', 'python-dateutil>=2.9.0.post0', 'types-python-dateutil>=2.9.0.20241206', 'keyring>=25.6.0', 'cachetools>=5.0.0', 'types-cachetools>=5.5.0.20240820'],
    keywords=["mseep"] + [],
)
