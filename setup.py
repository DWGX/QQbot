from setuptools import setup, find_packages

#pip freeze > requirements.txt

setup(
    name="QQbot",  # 包名
    version="1.0.0",  # 版本号
    author="Your Name",  # 作者
    author_email="dwgx1337@gmail.com",  # 作者邮箱
    description="A QQ bot Game Is DHH",  # 项目描述
    packages=find_packages(),  # 自动查找项目中的包
    include_package_data=True,  # 包括非Python文件
    install_requires=[  # 项目的依赖项（可选，如果有 `requirements.txt` 文件可以省略此部分）
        "botpy",
        "pyyaml",
        # 其他依赖项
    ],
    classifiers=[  # 分类信息，可选
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Python 版本要求
)
