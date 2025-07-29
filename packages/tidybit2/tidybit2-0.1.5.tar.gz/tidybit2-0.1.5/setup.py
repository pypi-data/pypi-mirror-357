from setuptools import setup, find_namespace_packages

setup(
    name="tidybit2",
    version="0.1.5",
    description="A command-line tool to organize files into system folders",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Kelly Forge",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "questionary",
        "colorama"  # Added for colored output
    ],
    entry_points={
        "console_scripts": [
            "organize = organizer.__main__:main"
        ]
    },
    python_requires=">=3.6",
)