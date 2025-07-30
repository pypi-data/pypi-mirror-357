
from setuptools import setup, find_packages

setup(
    name="mseep-serena",
    version="0.1.3",
    description="",
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
    install_requires=['requests>=2.32.3,<3', 'pyright>=1.1.396,<2', 'overrides>=7.7.0,<8', 'python-dotenv>=1.0.0, <2', 'mcp>=1.5.0', 'flask>=3.0.0', 'sensai-utils>=1.4.0', 'pydantic>=2.10.6', 'types-pyyaml>=6.0.12.20241230', 'pyyaml>=6.0.2', 'ruamel.yaml>=0.18.0', 'jinja2>=3.1.6', 'dotenv>=0.9.9', 'pathspec>=0.12.1', 'psutil>=7.0.0', 'docstring_parser>=0.16', 'joblib>=1.5.1', 'tqdm>=4.67.1'],
    keywords=["mseep"] + [],
)
