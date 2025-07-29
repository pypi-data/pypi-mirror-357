from setuptools import setup, find_packages

setup(
    name="tc-auto",  # 包名（pip install 时用）
    version="0.1.0",  # 版本号
    author="wanderingYee",
    author_email="yehongjiang2012@gmail.com",
    description="tencentcloud api自动化封装",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wanderingYee/TC-Auto",
    packages=find_packages(),  # 自动发现所有包
    install_requires=[  # 依赖项
        "requests==2.32.4",
    ],
    classifiers=[  # PyPI 分类标签
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Python 版本要求
)
