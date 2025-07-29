from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="json2png-annotation",
    version="0.1.0",
    author="Nguyen Tran",
    author_email="nguyentran4896@gmail.com",
    description="A library for converting JSON annotation files to PNG masks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nguyentran4896/json2png-annotation",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "Pillow>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "json2png=json2png_annotation.cli:main",
        ],
    },
) 