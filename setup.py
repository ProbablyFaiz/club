from setuptools import setup

setup(
    name="club",
    version="0.2.1",
    py_modules=["club"],
    install_requires=["click"],
    entry_points={
        "console_scripts": [
            "club=club:cli",
        ],
    },
    python_requires=">=3.6",
)
