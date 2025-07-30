from setuptools import setup, find_packages

setup(
    name="cync",
    version="0.1.0",
    description="Fast and efficient local file synchronization tool",
    author="Zachary Shonk",
    author_email="shonkzachary@gmail.com",
    url="https://github.com/ZacharyShonk/Cync",
    packages=find_packages(),
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "cync=cync.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
