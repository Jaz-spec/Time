from setuptools import setup, find_packages

setup(
    name="time-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "time=time_cli.cli:cli",
        ],
    },
    author="Your Name",
    description="A CLI-based timekeeping tool",
    python_requires=">=3.7",
)