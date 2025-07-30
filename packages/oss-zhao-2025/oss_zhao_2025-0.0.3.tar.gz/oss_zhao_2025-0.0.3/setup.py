import setuptools
from pathlib import Path

# 读取 README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="oss-zhao-2025",
    version="0.0.3",
    author="zhao",
    packages=setuptools.find_packages(), 
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",

    # 如果你只是有散落的 top-level 脚本（.py），就用 py_modules
    py_modules=[p.stem for p in Path(".").glob("*.py") if p.name not in ("setup.py", "MANIFEST.in")],

    # data_files 也可以，但这里用 package_data + include_package_data
    package_data={
        'chromedriver': ['chromedriver-linux64.zip', 'chromedriver-win64.zip'],
    },

    # # 如果希望自动给 main.py 生成一个命令行入口（可选）
    # entry_points={
    #     "console_scripts": [
    #         # 假设 main.py 里有个 main() 函数
    #         "oss-fuzz-main = main:main",
    #     ],
    # },

    python_requires=">=3.8",
    install_requires=[
        "selenium==4.27.1",
        "beautifulsoup4==4.9.1"
    ]
)
