from setuptools import setup, find_packages

setup(
    name="hermes",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["openai>=1.0.0", "click>=8.0.0", "rich>=13.0.0", "PyGithub>=2.0.0", "gitpython>=3.1.0"],
    entry_points={"console_scripts": ["hermes=hermes.cli:main"]},
    python_requires=">=3.10",
)
