from setuptools import setup, find_packages

setup(
    name="dodo-lookup",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "python-whois",
        "termcolor",
        "pyfiglet",
        "prettytable",
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "dodo = dodo.main:main",
        ],
    },
    python_requires=">=3.7",
)
