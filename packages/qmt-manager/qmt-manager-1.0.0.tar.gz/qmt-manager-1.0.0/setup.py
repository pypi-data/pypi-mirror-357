from setuptools import setup, find_packages
import os

# 读取 README.md 作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 检查并准备 xtquant 库（无需复制，直接包含）
def prepare_libs():
    src_path = os.path.join("xttrader_manager", "libs", "xtquant")
    if not os.path.exists(src_path) or not os.path.isdir(src_path) or not os.listdir(src_path):
        raise RuntimeError(f"xtquant 库路径 {src_path} 不存在或为空，请检查项目结构")
    print(f"✅ 使用项目内 xtquant 库: {src_path}")
    return True

if not prepare_libs():
    raise RuntimeError("xtquant 库准备失败")

setup(
    name='qmt-manager',  # 包名，建议小写且唯一
    version='1.0.0',     # 初始版本号
    author='量化交易汤姆猫',
    author_email='',  # 添加邮箱（可选）
    description='QMT_XTQUANT交易接口封装库 - 简化miniQMT使用',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',  # 项目主页（可选）
    packages=find_packages(),  # 自动查找包（会找到 xttrader_manager）
    include_package_data=True,  # 包含非代码文件
    package_data={
        'xttrader_manager': ['libs/xtquant/*', 'libs/xtquant/**/*'],  # 包含 xtquant 文件
    },
    install_requires=[
        'pandas>=1.0',
        'tabulate>=0.8.9',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # 根据实际许可证调整
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'xttrader-demo = xttrader_manager.manager:main',  # 确保有 main 函数
        ],
    },
    keywords='qmt xtquant trading',
)
