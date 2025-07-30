from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mainx",  # Change to your actual package name
    version="0.4",
    py_modules=["main1", "runner", "safe_runner"],
    entry_points={
        "console_scripts": [
            "mainx = runner:main",
            "mainx2 = safe_runner:main",
        ],
    },
    author="Your Name",
    description="Educational bug analysis tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
