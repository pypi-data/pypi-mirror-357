from setuptools import setup, find_packages

setup(
    name="pyjcli-beta",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "pydb=pydb.cli:main"
        ]
    },
    author="Punit Sinha",
    description="A simple JSON-based CLI database tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/punitsinha23/pydb",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6"
)
