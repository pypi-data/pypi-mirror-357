from setuptools import setup, find_packages
from setuptools.config.expand import entry_points

def get_version():
    with open("sap2assembler/__main__.py") as f:
        data = f.read()
        for line in data.split("\n"):
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().replace('"', "")
                return version

        raise Exception("error, version not found")

setup(
    name="sap2assembler",              # package name on PyPI
    version=get_version(),                   # current version
    packages=find_packages(),          # automatically find sap2assembler/ folder
    install_requires=[],               # if you needed any external libraries, list them here
    author="Samarth Javagal",                  # your name
    author_email="samarthjavagal@gmail.com", # optional, but PyPI asks
    description="A simple assembler for the SAP-2 computer architecture.",  # short description
    long_description=open('README.md').read(),  # your full readme file
    long_description_content_type="text/markdown",  # because you are using markdown
    url="https://github.com/samTheComputerArchitect/sap2assembler",  # GitHub link (if you have it)
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",    # or whichever you pick
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "sap2assembler=sap2assembler:main",
        ]
    }# minimum Python version
)
