import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="police_stop_and_search_api-HaeckelK",
    version="1.1.0",
    author="HaeckelK",
    author_email="author@example.com",
    description="Wrapper to get uk police stop and search data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HaeckelK/stop_and_search_api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
