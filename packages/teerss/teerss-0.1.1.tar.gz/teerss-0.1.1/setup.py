from setuptools import setup, find_packages

setup(
    name="teerss",
    version="0.1.1",
    author="Keith Henderson",
    description="A terminal-based RSS reader built with Rich",
    packages=find_packages(),
    install_requires=[
        "feedparser",
        "requests",
        "readability-lxml",
        "beautifulsoup4",
        "rich",
    ],
    entry_points={"console_scripts": ["teerss = teerss.main:main"]},
    python_requires=">=3.7",
)
