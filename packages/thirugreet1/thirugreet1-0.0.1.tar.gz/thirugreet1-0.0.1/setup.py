from setuptools import setup, find_packages

setup(
    name="thirugreet1",  # Change this if already taken on PyPI
    version="0.0.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple greeting package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/thirugreet1",  # Optional
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
