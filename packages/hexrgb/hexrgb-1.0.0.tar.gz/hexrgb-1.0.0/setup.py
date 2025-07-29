from setuptools import setup, find_packages

setup(
    name="hexrgb",
    version="1.0.0",
    packages=["hexrgb"],
    entry_points={
        "console_scripts": [
            "hexrgb = hexrgb.main:main",
        ],
    },
    author="Mallik Mohammad Musaddiq",
    description="Convert HEX color to RGB via CLI.",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)