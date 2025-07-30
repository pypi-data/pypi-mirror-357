from setuptools import setup, find_packages

setup(
    name="mtsl",       # must be unique on PyPI
    version="0.1.0.6",                # follow semantic versioning
    author="Preston Coley",
    author_email="prestoncoley0920@proton.me",
    description="An easy to use, minimal trust security layer.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyelle>=0.1.0",
        "cryptography>=45.0.3",
        "argon2-cffi>=25.1.0"
    ]
)