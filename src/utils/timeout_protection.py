"""
超时保护模块

提供程序运行时间监控和超时处理功能
"""

import threading
import time
import sys
import os
import signal
from typing import Optional, Callable
from datetime import datetime, timedelta
import logging


class TimeoutProtection:
    """超时保护类"""

    def __init__(self, timeout_seconds: int = 300):  # 默认5分钟
        """
        初始化超时保护

        Args:
            timeout_seconds: 超时时间（秒），默认300秒（5分钟）
        """
        self.timeout_seconds = timeout_seconds
        self.start_time: Optional[datetime] = None
        self.timer: Optional[threading.Timer] = None
        self.is_running = False
        self.timeout_callback: Optional[Callable] = None
        self.logger = logging.getLogger(__name__)

    def set_timeout_callback(self, callback: Callable):
        """
        设置超时回调函数

        Args:
            callback: 超时时调用的回调函数
        """
        self.timeout_callback = callback

    def start(self):
        """开始超时监控"""
        if self.is_running:
            self.logger.warning("超时保护已经在运行中")
            return

        self.start_time = datetime.now()
        self.is_running = True

        # 创建定时器
        self.timer = threading.Timer(self.timeout_seconds, self._timeout_handler)
        self.timer.daemon = True  # 设置为守护线程
        self.timer.start()

        self.logger.info(f"超时保护已启动，超时时间: {self.timeout_seconds}秒")

    def stop(self):
        """停止超时监控"""
        if not self.is_running:
            return

        self.is_running = False

        if self.timer and self.timer.is_alive():
            self.timer.cancel()

        elapsed_time = self._get_elapsed_time()
        self.logger.info(f"超时保护已停止，程序运行时间: {elapsed_time:.2f}秒")

    def _timeout_handler(self):
        """超时处理函数"""
        if not self.is_running:
            return

        elapsed_time = self._get_elapsed_time()
        self.logger.critical(
            f"程序运行超时！运行时间: {elapsed_time:.2f}秒，超时限制: {self.timeout_seconds}秒"
        )

        # 调用超时回调函数
        if self.timeout_callback:
            try:
                self.timeout_callback()
            except Exception as e:
                self.logger.error(f"执行超时回调函数时出错: {e}")

        # 强制终止程序
        self._force_terminate()

    def _get_elapsed_time(self) -> float:
        """获取已运行时间（秒）"""
        if not self.start_time:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()

    def get_remaining_time(self) -> float:
        """获取剩余时间（秒）"""
        if not self.is_running:
            return 0.0
        elapsed = self._get_elapsed_time()
        return max(0.0, self.timeout_seconds - elapsed)

    def get_status(self) -> dict:
        """获取超时保护状态"""
        return {
            "is_running": self.is_running,
            "timeout_seconds": self.timeout_seconds,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "elapsed_time": self._get_elapsed_time(),
            "remaining_time": self.get_remaining_time(),
        }

    def _force_terminate(self):
        """强制终止程序"""
        self.logger.critical("程序即将强制终止以防止卡死")

        try:
            # 在Windows系统上使用不同的终止方法
            if os.name == "nt":  # Windows
                os._exit(1)
            else:  # Unix/Linux
                os.kill(os.getpid(), signal.SIGTERM)
                time.sleep(1)  # 给程序一点时间优雅关闭
                os.kill(os.getpid(), signal.SIGKILL)
        except Exception as e:
            self.logger.error(f"强制终止程序时出错: {e}")
            # 最后的手段
            sys.exit(1)


class TimeoutProtectionManager:
    """超时保护管理器"""

    def __init__(self, app_instance=None):
        """
        初始化超时保护管理器

        Args:
            app_instance: 应用程序实例，用于发送紧急通知
        """
        self.app_instance = app_instance
        self.protection = TimeoutProtection()
        self.logger = logging.getLogger(__name__)

        # 设置超时回调
        self.protection.set_timeout_callback(self._emergency_notification)

    def start_protection(self, timeout_seconds: int = 300):
        """
        启动超时保护

        Args:
            timeout_seconds: 超时时间（秒）
        """
        self.protection.timeout_seconds = timeout_seconds
        self.protection.start()

    def stop_protection(self):
        """停止超时保护"""
        self.protection.stop()

    def _emergency_notification(self):
        """紧急通知处理"""
        self.logger.critical("触发紧急通知机制")

        if not self.app_instance:
            self.logger.warning("应用实例未设置，无法发送紧急通知")
            return

        try:
            # 获取当前日志文件路径
            log_file_path = None
            if (
                hasattr(self.app_instance, "logger_manager")
                and self.app_instance.logger_manager
            ):
                log_file_path = self.app_instance.logger_manager.get_current_log_file()

            # 发送紧急通知
            if (
                hasattr(self.app_instance, "telegram_notifier")
                and self.app_instance.telegram_notifier
            ):
                self._send_emergency_telegram_notification(log_file_path)
            else:
                self.logger.warning("Telegram通知器未配置，无法发送紧急通知")

        except Exception as e:
            self.logger.error(f"发送紧急通知时出错: {e}")

    def _send_emergency_telegram_notification(
        self, log_file_path: Optional[str] = None
    ):
        """发送紧急Telegram通知"""
        try:
            # 构建紧急通知消息
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elapsed_time = self.protection._get_elapsed_time()

            # 转义MarkdownV2格式的特殊字符
            def escape_markdown_v2(text):
                """转义MarkdownV2格式的特殊字符"""
                special_chars = [
                    "_",
                    "*",
                    "[",
                    "]",
                    "(",
                    ")",
                    "~",
                    "`",
                    ">",
                    "#",
                    "+",
                    "-",
                    "=",
                    "|",
                    "{",
                    "}",
                    ".",
                    "!",
                ]
                for char in special_chars:
                    text = text.replace(char, f"\\{char}")
                return text

            # 构建消息，转义特殊字符
            escaped_time = escape_markdown_v2(current_time)
            escaped_elapsed = escape_markdown_v2(f"{elapsed_time:.1f}")
            escaped_timeout = escape_markdown_v2(str(self.protection.timeout_seconds))

            message = f"""*🚨 98tang\\-autosign 程序超时通知*

*触发时间:* {escaped_time}
*运行时长:* {escaped_elapsed} 秒
*超时限制:* {escaped_timeout} 秒

*状态:* 程序已自动终止以防止卡死
*建议:* 请检查网络连接和系统状态，查看日志文件了解详情"""

            # 发送消息
            self.app_instance.telegram_notifier.send_message(message)
            self.logger.info("紧急Telegram通知已发送")

            # 强制发送日志文件（不管用户是否配置了发送日志）
            if log_file_path and os.path.exists(log_file_path):
                try:
                    self.app_instance.telegram_notifier.send_document(
                        document_path=log_file_path,
                        caption=f"📄 程序超时终止时的日志文件\n时间: {current_time}",
                    )
                    self.logger.info("紧急日志文件已发送")
                except Exception as e:
                    self.logger.error(f"发送紧急日志文件时出错: {e}")
            else:
                self.logger.warning(f"日志文件不存在或路径无效: {log_file_path}")

        except Exception as e:
            self.logger.error(f"发送紧急Telegram通知时出错: {e}")


# 上下文管理器，方便使用
class TimeoutProtectionContext:
    """超时保护上下文管理器"""

    def __init__(self, app_instance=None, timeout_seconds: int = 300):
        """
        初始化超时保护上下文

        Args:
            app_instance: 应用程序实例
            timeout_seconds: 超时时间（秒）
        """
        self.manager = TimeoutProtectionManager(app_instance)
        self.timeout_seconds = timeout_seconds

    def __enter__(self):
        """进入上下文"""
        self.manager.start_protection(self.timeout_seconds)
        return self.manager

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        self.manager.stop_protection()
        return False  # 不抑制异常
