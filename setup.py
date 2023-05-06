from setuptools import setup

setup(
    name="club",
    version="0.1.0",
    py_modules=["club"],
    install_requires=["click"],
    entry_points={
        "console_scripts": [
            "club=club:cli",
        ],
    },
)
