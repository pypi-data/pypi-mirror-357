from setuptools import setup, find_packages
import os

# 读取README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='qmt-manager',
    version='1.0.2',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    author='量化交易汤姆猫',
    description='QMT_XTQUANT交易接口封装库',
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,  # ✅ 关键
    
    # 修复1: 正确包名
    package_data={
        'qmt_manager': [
            # 修复2: 包含二进制文件类型
            'libs/xtquant/*.pyd',  
            'libs/xtquant/*.dll',
            'libs/xtquant/**/*.dll',
            'libs/xtquant/**/*.so',
            # 包含所有子目录
            'libs/xtquant/**/*',
        ],
    },
    
    install_requires=[
        'pandas>=1.0',
        'tabulate>=0.8.9',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",  # 增加Windows限定
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'qmt-manager = qmt_manager.manager:main',
        ],
    },
    license='MIT',
    license_files=('LICENSE.md',),
)