from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mainx",
    version="0.8",
    py_modules=["main1", "runner", "safe_runner"],
    entry_points={
        "console_scripts": [
            "mainx = runner:main",
            "mainx2 = safe_runner:main",
        ],
    },
    author="Your Name",
    description="Educational tool with network, system, and Discord webhook support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "discord.py>=2.0.0",
        'pywin32; platform_system=="Windows"',
    ],
)
