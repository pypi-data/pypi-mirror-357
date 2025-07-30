
from setuptools import setup, find_packages

setup(
    name="mseep-arxiv-paper-mcp",
    version="0.1.5",
    description="arXiv 논문 데이터를 Claude AI와 연동하는 MCP 서버",
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
    install_requires=['mcp[cli]>=1.6.0', 'requests>=2.0.0', 'beautifulsoup4>=4.0.0', 'lxml>=4.0.0'],
    keywords=["mseep"] + ['arxiv', 'claude', 'ai', 'research', 'papers'],
)
