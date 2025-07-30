from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mainx',  # Change this to your unique package name
    version='0.1',
    py_modules=['main1', 'runner'],
    entry_points={
        'console_scripts': [
            'mainx = runner:main',
        ],
    },
    author="Your Name",
    description="Educational bug simulation tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
