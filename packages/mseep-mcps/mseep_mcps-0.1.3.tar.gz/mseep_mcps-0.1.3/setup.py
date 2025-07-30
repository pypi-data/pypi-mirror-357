
from setuptools import setup, find_packages

setup(
    name="mseep-mcps",
    version="0.1.3",
    description="Model Context Protocol server for continue.dev",
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
    install_requires=['fastmcp>=2.8.1', 'lancedb>=0.4.0', 'markdown>=3.4.0', 'rank_bm25', 'python-dotenv>=1.0.0', 'python-frontmatter>=1.1.0'],
    keywords=["mseep"] + [],
)
