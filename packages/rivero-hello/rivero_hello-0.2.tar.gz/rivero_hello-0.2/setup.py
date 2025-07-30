from setuptools import setup, find_packages

setup(
    name='rivero_hello',
    version='0.2',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "rivero-hello = rivero_hello:hello",
        ],
    },
)