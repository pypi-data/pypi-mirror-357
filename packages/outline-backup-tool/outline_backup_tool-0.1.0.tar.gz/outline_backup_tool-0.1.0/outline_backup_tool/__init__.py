# outline_backup_tool/__init__.py

import logging

# --- 1. 定义包的版本号 (Single Source of Truth) ---
# setup.py 会从这里读取版本号
__version__ = "0.1.0"

# --- 2. 暴露包的主要接口 ---
# 这样用户可以直接通过 `from outline_backup_tool import OutlineBackup` 来使用
from .backup import OutlineBackup

# --- 3. 定义当 `from outline_backup_tool import *` 时导入哪些内容 ---
__all__ = [
    "OutlineBackup",
    "__version__",
]

# --- 4. (推荐) 为库配置日志，防止没有配置日志时出现警告 ---
# 这是一个非常好的实践，可以避免给库的使用者带来困惑
logging.getLogger(__name__).addHandler(logging.NullHandler())
