# setup.py

import os
import re
from setuptools import setup, find_packages

# --- 1. 安全地读取版本号 ---
# 从 __init__.py 文件中读取版本号，而不需要执行它
def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py_path = os.path.join(package, '__init__.py')
    with open(init_py_path, 'r', encoding='utf-8') as f:
        version_match = re.search(r"""^__version__\s*=\s*['"]([^'"]*)['"]""", f.read(), re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")

# --- 2. 读取 README 文件作为详细描述 ---
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A tool to backup Outline wiki instances."


setup(
    # --- 基础信息 ---
    name="outline-backup-tool",
    version=get_version("outline_backup_tool"),
    
    author="lanpangzi",
    author_email="yywfqq@live.com",
    
    # --- 描述信息 ---
    description="一个用于备份 Outline Wiki 实例的 Python 工具",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # --- 链接 ---
    url="https://github.com/bestbugwriter/outline-backup-tool",
    project_urls={
        "Bug Tracker": "https://github.com/bestbugwriter/outline-backup-tool/issues",
    },

    # --- 包配置 ---
    # 自动查找项目中的所有包，这里会找到 'outline_backup_tool'
    packages=find_packages(exclude=["tests*", "*.tests"]),
    
    # 声明此包所需的 Python 版本
    python_requires=">=3.7",

    # --- 依赖项 ---
    # 在这里列出你的工具所依赖的第三方库
    # pip 在安装你的包时，会自动安装这些依赖
    install_requires=[
        "requests>=2.25.0",
        # "tqdm", # 如果需要进度条，可以取消注释
    ],

    # --- 命令行工具入口 ---
    # 这个配置会让用户在安装后，可以直接在命令行运行 `outline-backup`
    entry_points={
        "console_scripts": [
            "outline-backup=outline_backup_tool.cli:main",
        ],
    },

    license="MIT",

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: Utilities",
    ],
)
