from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="worldmapper",
    version="0.1.1",
    author="Fatih Koçkesen",
    author_email="fatihinemaili@gmail.com",
    description="A Python package for accessing world country, state, and city information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fatih-koc/worldmapper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    package_data={
        "worldmapper": ["world.json"],
    },
)