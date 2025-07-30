请将下面的文本保存为项目根目录下的 README.md 文件。您可以根据需要进行调整和补充。

Markdown

# Outline Wiki Backup Tool

[![PyPI version](https://badge.fury.io/py/outline-backup-tool.svg)](https://badge.fury.io/py/outline-backup-tool) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`outline-backup-tool` 是一个 Python 工具，用于备份自建的 [Outline](https://www.getoutline.com/) Wiki 服务实例。它支持导出所有集合、检查备份状态、下载备份文件（支持本地存储和 S3 存储下载方式）以及删除远程服务器上的备份。

## 主要功能

* **全量导出**: 备份 Outline Wiki 中的所有集合。
* **状态检查**: 监控导出任务的实时状态。
* **灵活下载**:
    * 支持从配置为**本地存储**的 Outline 实例直接下载备份文件。
    * 支持从配置为 **S3 兼容对象存储**的 Outline 实例下载备份文件（通过重定向获取 S3 URL）。
* **自动清理**: 可选在成功下载备份后自动删除远程服务器上的备份文件。
* **多种导出格式**: 支持 `json` 和 `outline-markdown` 导出格式。
* **配置灵活**: 可以通过命令行参数或环境变量配置 Outline 主机名、API 密钥等。
* **可作为库使用**: 也可以在其他 Python 项目中作为库导入和使用。

## 安装

### 前提条件

* Python 3.7 或更高版本。

### 使用 pip 安装

如果您将此工具发布到 PyPI，用户可以通过以下方式安装：
```bash
pip install outline-backup-tool
在此之前，您可以从本地项目目录安装：

Bash

pip install .
使用方法
该工具既可以作为命令行工具使用，也可以作为 Python 库集成到其他脚本中。

1. 命令行接口 (CLI)
安装后，您可以直接从命令行运行备份。

基本用法:

Bash

python -m outline_backup_tool.backup --hostname "your.outline.host" --token "YOUR_API_TOKEN"
或者，如果在 setup.py 中配置了 entry_points 并正确安装，可以直接使用脚本名：

Bash

# 假设 entry_point 配置为 outline-backup
# outline-backup --hostname "your.outline.host" --token "YOUR_API_TOKEN"
必填参数:

--hostname YOUR_OUTLINE_HOSTNAME: 您的 Outline 实例域名 (例如 wiki.example.com)。
--token YOUR_OUTLINE_API_TOKEN: 您的 Outline API 密钥。
可选参数:

--format {json,outline-markdown}: 导出格式 (默认为: json)。
--dir BACKUP_DIRECTORY: 本地备份文件存储目录 (默认为: outline_backups)。
--storage-type {direct,s3}: Outline 实例的存储后端类型 (默认为: direct)。
direct: 当 Outline 使用服务器本地存储时选择此项。
s3: 当 Outline 使用 S3 或 S3 兼容对象存储时选择此项。
--no-delete: 设置此标志后，在成功下载备份后不会删除服务器上的远程备份文件。
--debug: 启用 DEBUG 级别的日志输出，以显示更详细的信息。
示例:

备份到指定目录，使用 S3 存储类型，并且下载后不删除远程备份：

Bash

python -m outline_backup_tool.backup \
    --hostname "wiki.mycompany.com" \
    --token "xxxxxxxxxxxxxxx" \
    --format "outline-markdown" \
    --dir "/mnt/backups/outline" \
    --storage-type "s3" \
    --no-delete \
    --debug
2. 作为 Python 库使用
您也可以在自己的 Python 脚本中导入并使用 OutlineBackup 类。

Python

import logging
import os
from outline_backup_tool import OutlineBackup, outline_logger

# 配置日志 (可选, 如果您的应用已经配置了日志则不需要)
# outline_logger.setLevel(logging.DEBUG) # 设置库的日志级别
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ---- 配置 ----
# 建议从环境变量或安全配置中读取敏感信息
OUTLINE_HOSTNAME = os.environ.get("OUTLINE_HOSTNAME", "your.outline.host")
OUTLINE_TOKEN = os.environ.get("OUTLINE_TOKEN", "YOUR_API_TOKEN")
EXPORT_FORMAT = "json"  # 或 "outline-markdown"
BACKUP_DIR = "my_wiki_backups"
# "direct" 适用于 Outline 本地存储, "s3" 适用于 S3 存储
STORAGE_TYPE = "direct" # 或 "s3"

if OUTLINE_HOSTNAME == "your.outline.host" or OUTLINE_TOKEN == "YOUR_API_TOKEN":
    logging.warning("请先配置 OUTLINE_HOSTNAME 和 OUTLINE_TOKEN")
else:
    try:
        backup_client = OutlineBackup(
            hostname=OUTLINE_HOSTNAME,
            secret_token=OUTLINE_TOKEN,
            export_format=EXPORT_FORMAT,
            export_dir=BACKUP_DIR
        )

        # 运行备份，成功下载后删除远程备份 (delete_after_download=True)
        downloaded_file_path = backup_client.run_backup(
            storage_type=STORAGE_TYPE,
            delete_after_download=True
        )

        if downloaded_file_path:
            logging.info(f"备份成功！文件保存在: {downloaded_file_path}")
        else:
            logging.error("备份失败。")

    except ValueError as ve:
        logging.error(f"配置错误: {ve}")
    except Exception as e:
        logging.error(f"发生意外错误: {e}", exc_info=True) # exc_info=True 在 DEBUG 模式下更佳

配置环境变量 (推荐用于敏感信息)
您可以将敏感信息（如 API 密钥）设置为环境变量，以避免将其硬编码到脚本或命令行历史中：

OUTLINE_HOSTNAME: Outline 服务的主机名。
OUTLINE_TOKEN: Outline API 密钥。
脚本中的示例代码已包含从环境变量读取这些值的逻辑。

如何获取 Outline API Token?
登录到您的 Outline 实例。
转到 "Settings" -> "API tokens"。
点击 "Create new API token"。
给它一个描述性的名字，然后点击 "Create"。
立即复制生成的 token。关闭此窗口后，您将无法再次看到它。
许可证
该项目使用 MIT 许可证。

贡献
欢迎提交 Pull Request。对于重大更改，请先开启一个 issue 来讨论您想要更改的内容。


