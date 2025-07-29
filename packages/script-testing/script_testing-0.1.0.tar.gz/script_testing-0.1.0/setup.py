from setuptools import setup, find_packages

setup(
    name="script_testing",
    version="0.1.0",
    description="A simple Python package for greeting",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)

