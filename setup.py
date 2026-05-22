import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wii-remote-pkg",
    version="2.0.0",
    author="cerealpine",
    description="Package to interact with a Wii Remote for Windows computers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cerealpine/wii-remote-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows 11",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "hidapi",
    ],
)
