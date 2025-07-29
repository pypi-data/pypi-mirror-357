from setuptools import setup, find_packages

setup(
    name="tydybit2",
    version="0.1.1",  # Start with this, bump later
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["questionary"],
    entry_points={
        "console_scripts": [
            "organize = organizer.__main__:main",
        ],
    },
    author="Kelly",
    author_email="your.email@example.com",
    description="A CLI tool to organize files into system and custom folders",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",  # Pick a license
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)