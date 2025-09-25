"""
编码处理工具模块

提供安全的编码处理函数，确保在不同环境中的兼容性
"""

import logging
import os
from typing import Optional


class EncodingHelper:
    """编码处理辅助类"""

    @staticmethod
    def safe_write_text(file_path: str, content: str, encoding: str = "utf-8") -> bool:
        """
        安全地写入文本文件

        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 编码格式，默认utf-8

        Returns:
            是否写入成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 清理内容中的问题字符
            clean_content = EncodingHelper.clean_text_for_encoding(content)

            with open(file_path, "w", encoding=encoding, errors="replace") as f:
                f.write(clean_content)
            return True
        except Exception as e:
            logging.warning(f"安全写入文件失败 {file_path}: {e}")
            return False

    @staticmethod
    def safe_read_text(file_path: str, encoding: str = "utf-8") -> Optional[str]:
        """
        安全地读取文本文件

        Args:
            file_path: 文件路径
            encoding: 编码格式，默认utf-8

        Returns:
            文件内容，失败时返回None
        """
        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                return f.read()
        except Exception as e:
            logging.warning(f"安全读取文件失败 {file_path}: {e}")
            return None

    @staticmethod
    def clean_text_for_encoding(text: str) -> str:
        """
        清理文本中可能导致编码问题的字符

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        if not text:
            return text

        try:
            # 先尝试编码解码来清理问题字符
            clean_text = text.encode("utf-8", errors="replace").decode("utf-8")

            # 移除或替换可能的代理对字符
            # 代理对字符范围: \uD800-\uDFFF
            import re

            clean_text = re.sub(r"[\uD800-\uDFFF]", "?", clean_text)

            return clean_text
        except Exception as e:
            logging.warning(f"文本清理失败: {e}")
            # 如果清理失败，返回原文本
            return text

    @staticmethod
    def setup_encoding_environment():
        """
        设置编码环境变量，确保Python正确处理UTF-8
        """
        import os

        # 设置Python编码环境变量
        env_vars = {
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
        }

        for key, value in env_vars.items():
            if key not in os.environ:
                os.environ[key] = value
                logging.debug(f"设置编码环境变量: {key}={value}")

    @staticmethod
    def is_valid_utf8(text: str) -> bool:
        """
        检查文本是否为有效的UTF-8

        Args:
            text: 要检查的文本

        Returns:
            是否为有效UTF-8
        """
        try:
            text.encode("utf-8")
            return True
        except UnicodeEncodeError:
            return False

    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        获取安全的文件名，移除可能导致问题的字符

        Args:
            filename: 原始文件名

        Returns:
            安全的文件名
        """
        import re

        # 移除或替换不安全的字符
        safe_filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # 确保文件名不以点开头或结尾
        safe_filename = safe_filename.strip(".")

        # 限制文件名长度
        if len(safe_filename) > 200:
            safe_filename = safe_filename[:200]

        return safe_filename or "unnamed_file"
