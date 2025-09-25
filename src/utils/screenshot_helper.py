"""
截图发送辅助工具模块

提供统一的截图发送功能，避免代码重复
"""

import logging
import os
from typing import Optional
from selenium.webdriver.chrome.webdriver import WebDriver
from src.notifications.telegram import TelegramNotifier


class ScreenshotHelper:
    """截图发送辅助类"""

    def __init__(self, telegram_notifier: Optional[TelegramNotifier] = None):
        """
        初始化截图助手

        Args:
            telegram_notifier: Telegram通知器实例
        """
        self.telegram_notifier = telegram_notifier
        self.logger = logging.getLogger(__name__)

    def capture_and_send_screenshot(
        self,
        driver: WebDriver,
        scenario: str,
        description: str = "",
        send_to_telegram: bool = True,
    ) -> Optional[str]:
        """
        截取屏幕截图并发送到Telegram

        Args:
            driver: WebDriver实例
            scenario: 截图场景标识
            description: 截图描述
            send_to_telegram: 是否发送到Telegram

        Returns:
            截图文件路径，如果失败返回None
        """
        screenshot_path = None

        try:
            # 确保日志目录存在
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)

            # 生成截图文件名
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f"{scenario}_{timestamp}.png"
            screenshot_path = os.path.join(log_dir, screenshot_filename)

            # 截取截图
            if driver.save_screenshot(screenshot_path):
                self.logger.info(f"截图已保存: {screenshot_path}")

                # 发送到Telegram（如果启用）
                if send_to_telegram and self.telegram_notifier:
                    caption = (
                        f"📸 {description or scenario}"
                        if description
                        else f"📸 {scenario}"
                    )

                    if self.telegram_notifier.send_screenshot(screenshot_path, caption):
                        self.logger.info(f"截图已发送到Telegram: {caption}")
                    else:
                        self.logger.warning("发送截图到Telegram失败")

                return screenshot_path
            else:
                self.logger.error("截图保存失败")
                return None

        except Exception as e:
            self.logger.error(f"截图处理失败: {e}")
            return None

    def send_existing_screenshot(
        self,
        screenshot_path: str,
        description: str = "",
    ) -> bool:
        """
        发送已存在的截图文件到Telegram

        Args:
            screenshot_path: 截图文件路径
            description: 截图描述

        Returns:
            发送是否成功
        """
        if not self.telegram_notifier:
            self.logger.warning("Telegram通知器未配置，无法发送截图")
            return False

        if not os.path.exists(screenshot_path):
            self.logger.error(f"截图文件不存在: {screenshot_path}")
            return False

        try:
            caption = f"📸 {description}" if description else "📸 截图"
            return self.telegram_notifier.send_screenshot(screenshot_path, caption)
        except Exception as e:
            self.logger.error(f"发送截图失败: {e}")
            return False

    def cleanup_old_screenshots(self, max_files: int = 10) -> None:
        """
        清理旧的截图文件

        Args:
            max_files: 保留的最大文件数
        """
        try:
            log_dir = "logs"
            if not os.path.exists(log_dir):
                return

            # 获取所有截图文件
            screenshot_files = [
                f
                for f in os.listdir(log_dir)
                if f.endswith(".png")
                and ("error_" in f or "execution_" in f or "lockout_" in f)
            ]

            if len(screenshot_files) <= max_files:
                return

            # 按修改时间排序，删除最旧的文件
            screenshot_files.sort(
                key=lambda x: os.path.getmtime(os.path.join(log_dir, x))
            )

            files_to_delete = screenshot_files[:-max_files]
            for filename in files_to_delete:
                try:
                    filepath = os.path.join(log_dir, filename)
                    os.remove(filepath)
                    self.logger.debug(f"已删除旧截图: {filename}")
                except Exception as e:
                    self.logger.warning(f"删除截图文件失败 {filename}: {e}")

        except Exception as e:
            self.logger.error(f"清理截图文件失败: {e}")

    @staticmethod
    def get_screenshot_filename(scenario: str, timestamp: Optional[str] = None) -> str:
        """
        生成标准化的截图文件名

        Args:
            scenario: 场景标识
            timestamp: 时间戳，如果不提供则使用当前时间

        Returns:
            截图文件名
        """
        if not timestamp:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return f"{scenario}_{timestamp}.png"
