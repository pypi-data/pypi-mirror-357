from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="sparkflint",
    description="SparkFlintCLI facilita a gestão de aplicações Apache Spark em ambientes remotos.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="1.0.1",
    url="https://github.com/RibeiroWiliam/sparkflint-cli",
    author="Wiliam Ribeiro",
    author_email="wiliamribeiro.tj@gmail.com",
    scripts=["scripts/sparkflint"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["typer[all]", "requests[all]", "rich", "toml", "cryptography"],
    entry_points={
        "console_scripts": [
            "sparkflint=sparkflintcli.main:app",
        ],
    },
    include_package_data=True,
)
