from setuptools import setup, find_packages

setup(
    name="ini2json",
    version="1.0.0",
    author="@readwithai",
    author_email="talwrii@gmail.com",
    description="Convert INI files to JSON and back for easy CLI tooling",
    packages=find_packages(),
    python_requires='>=3.7',
    entry_points={
        "console_scripts": [
            "ini2json=ini2json.main:ini2json",
            "json2ini=ini2json.main:json2ini",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
