from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vaultix-ssh",
    version="1.0.0",
    author="tusharmohanpuria1711@gmail.com",
    author_email="",
    description="A modern SSH connection manager with built-in agent support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tusharmohanpuria/Vaultix-SSH",
    packages=find_packages(include=['vaultix', 'vaultix.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    entry_points={
    'console_scripts': [
        'vaultix=vaultix.cli:main',
        ],
    },
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "pycryptodome>=3.15.0",
        "appdirs>=1.4.4",
    ],
)