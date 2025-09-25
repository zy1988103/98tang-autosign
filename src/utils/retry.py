"""
重试管理模块

提供操作重试逻辑
"""

from typing import Dict


class RetryManager:
    """重试管理器"""

    def __init__(self, max_retries: int = 3):
        """
        初始化重试管理器

        Args:
            max_retries: 最大重试次数
        """
        self.max_retries = max_retries
        self.counters: Dict[str, int] = {}

    def can_retry(self, operation: str) -> bool:
        """
        检查操作是否可以重试

        Args:
            operation: 操作名称

        Returns:
            是否可以重试
        """
        self.counters[operation] = self.counters.get(operation, 0) + 1
        return self.counters[operation] <= self.max_retries

    def reset(self, operation: str) -> None:
        """
        重置指定操作的重试计数器

        Args:
            operation: 操作名称
        """
        self.counters[operation] = 0

    def reset_all(self) -> None:
        """重置所有操作的重试计数器"""
        self.counters.clear()

    def get_retry_count(self, operation: str) -> int:
        """
        获取指定操作的重试次数

        Args:
            operation: 操作名称

        Returns:
            重试次数
        """
        return self.counters.get(operation, 0)

    def get_remaining_retries(self, operation: str) -> int:
        """
        获取指定操作的剩余重试次数

        Args:
            operation: 操作名称

        Returns:
            剩余重试次数
        """
        return max(0, self.max_retries - self.counters.get(operation, 0))
