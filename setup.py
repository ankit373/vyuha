from setuptools import setup, find_packages

setup(
    name="vyuha",
    version="0.1.0",
    packages=find_packages(),
    py_modules=['main'],
    install_requires=[
        "httpx",
        "typer",
        "rich",
        "python-dotenv",
        "PyYAML",
    ],
    entry_points={
        "console_scripts": [
            "vyuha=main:app",
        ],
    },
    author="Ankit Jha",
    description="An elite high-governance multi-agent engine.",
    license="MIT",
    keywords="multi-agent, ai, governance, orchestrator",
)
