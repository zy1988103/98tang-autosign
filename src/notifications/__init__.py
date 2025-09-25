"""
通知模块

提供各种通知方式的统一接口
"""

from .telegram import TelegramNotifier, NotificationData

__all__ = ["TelegramNotifier", "NotificationData"]
