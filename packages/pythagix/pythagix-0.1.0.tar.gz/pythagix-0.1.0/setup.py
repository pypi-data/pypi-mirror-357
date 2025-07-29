from setuptools import setup, find_packages

setup(
    name="pythagix",
    version="0.1.0",
    author="Your Name",
    description="A mathy Python package with utilities like LCM, triangle numbers, etc.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
