import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="my_module",
    version="0.0.1",
    author="Jean-Romain Roy",
    author_email="roy.jeanromain@gmail.com",
    description="Detects things in an image in an image",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeanromainroy/my-module",
    packages=['my_module'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: proprietary and confidential",
        "Operating System :: UNIX",
    ],
    install_requires=[
        'numpy',
    ],
    python_requires='>=3.6',
)