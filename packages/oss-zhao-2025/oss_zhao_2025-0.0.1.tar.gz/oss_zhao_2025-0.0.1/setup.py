import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name="oss-zhao-2025",
    version="0.0.1",
    author="zhao",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    package_data={
        'chromedriver':['*.zip','chromedriver-win64/*.chromedriver']
    },
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
)