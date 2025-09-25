"""
日志管理模块

统一的日志配置和管理
"""

import logging
import sys
import os
import glob
from datetime import datetime
from typing import Optional


class LoggerManager:
    """日志管理器"""

    _instance: Optional["LoggerManager"] = None
    _logger: Optional[logging.Logger] = None
    _current_log_file: Optional[str] = None

    def __new__(cls) -> "LoggerManager":
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def setup_logger(
        self,
        name: str = __name__,
        log_level: str = "INFO",
        log_dir: str = "logs",
        max_log_files: int = 7,
        debug_mode: bool = False,
    ) -> logging.Logger:
        """
        设置日志系统

        Args:
            name: 日志器名称
            log_level: 日志级别
            log_dir: 日志文件目录
            max_log_files: 最大日志文件数量
            debug_mode: 是否为调试模式

        Returns:
            配置好的日志器
        """
        if self._logger is not None:
            return self._logger

        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)

        # 清理旧日志文件
        self._cleanup_old_logs(log_dir, max_log_files)

        # 生成带时间戳的日志文件名（使用微秒确保唯一性）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        log_file = os.path.join(log_dir, f"98tang-autosign_{timestamp}.log")
        self._current_log_file = log_file

        # 日志级别映射
        level_mapping = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
        }
        log_level_obj = level_mapping.get(log_level, logging.INFO)

        # 如果是调试模式，强制使用DEBUG级别
        if debug_mode:
            log_level_obj = logging.DEBUG

        # 创建格式化器
        if log_level_obj == logging.DEBUG:
            # 调试模式：详细格式，包含函数名和行号
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            # 正常模式：简洁格式
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        # 设置根日志级别
        logging.basicConfig(level=log_level_obj, handlers=[])
        self._logger = logging.getLogger(name)
        self._logger.handlers.clear()

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        self._logger.setLevel(log_level_obj)

        # 写入初始化日志，确保文件不为空
        self._logger.info("98tang-autosign 日志系统初始化完成")
        if debug_mode:
            self._logger.debug(f"日志文件: {log_file}")
            self._logger.debug(f"日志级别: {log_level}")

        return self._logger

    def get_logger(self) -> Optional[logging.Logger]:
        """获取日志器"""
        return self._logger

    def get_current_log_file(self) -> Optional[str]:
        """获取当前日志文件路径"""
        return self._current_log_file

    def _cleanup_old_logs(self, log_dir: str, max_files: int) -> None:
        """
        清理旧日志文件

        Args:
            log_dir: 日志目录
            max_files: 最大保留文件数量
        """
        try:
            # 获取所有日志文件
            new_pattern = os.path.join(log_dir, "98tang-autosign_*.log")
            old_pattern = os.path.join(log_dir, "autosign_*.log")

            new_log_files = glob.glob(new_pattern)
            old_log_files = glob.glob(old_pattern)

            # 合并所有日志文件
            all_log_files = new_log_files + old_log_files

            # 过滤掉空文件（可能是初始化失败的文件）
            valid_log_files = []
            empty_log_files = []

            for file_path in all_log_files:
                try:
                    if os.path.getsize(file_path) > 0:
                        valid_log_files.append(file_path)
                    else:
                        empty_log_files.append(file_path)
                except OSError:
                    # 文件不存在或无法访问，跳过
                    continue

            # 删除空日志文件
            for empty_file in empty_log_files:
                try:
                    os.remove(empty_file)
                    print(f"已删除空日志文件: {os.path.basename(empty_file)}")
                except OSError as e:
                    print(f"删除空日志文件失败 {os.path.basename(empty_file)}: {e}")

            # 按修改时间排序，最新的在前
            valid_log_files.sort(key=os.path.getmtime, reverse=True)

            # 删除超出数量的旧文件
            if len(valid_log_files) >= max_files:
                files_to_delete = valid_log_files[
                    max_files - 1 :
                ]  # 为新文件预留1个位置
                for file_path in files_to_delete:
                    try:
                        os.remove(file_path)
                        print(f"已删除旧日志文件: {os.path.basename(file_path)}")
                    except OSError as e:
                        print(f"删除日志文件失败 {os.path.basename(file_path)}: {e}")

            final_count = min(len(valid_log_files), max_files)
            print(f"日志清理完成，当前保留 {final_count} 个日志文件")

        except Exception as e:
            print(f"清理日志文件时出错: {e}")

    @staticmethod
    def create_logger(
        name: str = __name__,
        log_level: str = "INFO",
        log_dir: str = "logs",
        max_log_files: int = 7,
        debug_mode: bool = False,
    ) -> logging.Logger:
        """
        创建日志器的便捷方法

        Args:
            name: 日志器名称
            log_level: 日志级别
            log_dir: 日志文件目录
            max_log_files: 最大日志文件数量
            debug_mode: 是否为调试模式

        Returns:
            配置好的日志器
        """
        manager = LoggerManager()
        return manager.setup_logger(name, log_level, log_dir, max_log_files, debug_mode)
