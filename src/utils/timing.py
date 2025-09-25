"""
时间管理模块

智能延迟管理器，让操作更像真人
"""

import time
import random
import logging
from typing import Dict, Tuple, Optional

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class TimingManager:
    """智能延迟管理器"""

    # 操作类型常量
    CLICK_DELAY = "click"
    SCROLL_DELAY = "scroll"
    TYPING_DELAY = "typing"
    PAGE_LOAD_DELAY = "page_load"
    READING_DELAY = "reading"
    NAVIGATION_DELAY = "navigation"
    REPLY_INTERVAL_DELAY = "reply_interval"

    # 全局延迟倍数
    _global_multiplier = 1.0

    # 延迟配置
    DELAY_CONFIGS: Dict[str, Tuple[float, float]] = {
        CLICK_DELAY: (0.3, 0.8),  # 点击前后的短暂停顿
        SCROLL_DELAY: (0.4, 1.2),  # 滚动间隔
        TYPING_DELAY: (0.1, 0.3),  # 打字间隔
        PAGE_LOAD_DELAY: (1.0, 2.5),  # 页面加载等待
        READING_DELAY: (0.8, 2.0),  # 阅读内容时的停顿
        NAVIGATION_DELAY: (0.5, 1.5),  # 导航切换
        REPLY_INTERVAL_DELAY: (15.0, 20.0),  # 回帖之间的间隔
    }

    # 动态评论间隔配置
    _comment_interval_seconds = 15  # 默认15秒

    @classmethod
    def set_global_multiplier(cls, multiplier: float) -> None:
        """
        设置全局延迟倍数

        Args:
            multiplier: 延迟倍数，限制在0.1-5.0之间
        """
        cls._global_multiplier = max(0.1, min(5.0, multiplier))

    @classmethod
    def set_comment_interval(cls, seconds: int) -> None:
        """
        设置评论间隔时间

        Args:
            seconds: 间隔秒数，强制不低于15秒
        """
        cls._comment_interval_seconds = max(15, seconds)
        # 动态更新REPLY_INTERVAL_DELAY配置
        base_interval = cls._comment_interval_seconds
        cls.DELAY_CONFIGS[cls.REPLY_INTERVAL_DELAY] = (
            base_interval,
            base_interval + 5.0,  # 基础间隔 + 最多5秒随机
        )

    @classmethod
    def smart_wait(
        cls,
        delay_type: str,
        multiplier: float = 1.0,
        logger: Optional[logging.Logger] = None,
    ) -> float:
        """
        智能等待，根据操作类型动态调整延迟

        Args:
            delay_type: 延迟类型
            multiplier: 额外的倍数调整
            logger: 日志器

        Returns:
            实际等待时间
        """
        if delay_type not in cls.DELAY_CONFIGS:
            delay_type = cls.CLICK_DELAY

        min_delay, max_delay = cls.DELAY_CONFIGS[delay_type]

        # 应用倍数调整（包括全局倍数）
        total_multiplier = multiplier * cls._global_multiplier
        min_delay *= total_multiplier
        max_delay *= total_multiplier

        # 生成更自然的随机延迟
        if NUMPY_AVAILABLE:
            try:
                # Beta分布参数：alpha=2, beta=3 使得分布偏向较小值
                beta_sample = np.random.beta(2, 3)
                wait_time = min_delay + (max_delay - min_delay) * beta_sample
            except Exception:
                # 如果numpy使用失败，回退到uniform分布
                wait_time = random.uniform(min_delay, max_delay)
        else:
            # 如果numpy不可用，使用uniform分布
            wait_time = random.uniform(min_delay, max_delay)

        if logger:
            logger.debug(f"{delay_type}延迟: {wait_time:.2f}秒")

        time.sleep(wait_time)
        return wait_time

    @classmethod
    def adaptive_wait(
        cls,
        base_delay_type: str,
        page_complexity: str = "normal",
        logger: Optional[logging.Logger] = None,
    ) -> float:
        """
        自适应等待，根据页面复杂度调整延迟

        Args:
            base_delay_type: 基础延迟类型
            page_complexity: 页面复杂度 (simple/normal/complex/heavy)
            logger: 日志器

        Returns:
            实际等待时间
        """
        complexity_multipliers = {
            "simple": 0.7,  # 简单页面，加载快
            "normal": 1.0,  # 正常页面
            "complex": 1.4,  # 复杂页面，需要更多时间
            "heavy": 1.8,  # 重型页面（如大量图片/视频）
        }

        multiplier = complexity_multipliers.get(page_complexity, 1.0)
        return cls.smart_wait(base_delay_type, multiplier, logger)

    @staticmethod
    def wait_for_page_ready(
        driver, timeout: int = 10, logger: Optional[logging.Logger] = None
    ) -> bool:
        """
        等待页面完全加载就绪

        Args:
            driver: WebDriver实例
            timeout: 超时时间
            logger: 日志器

        Returns:
            是否加载完成
        """
        try:
            from selenium.webdriver.support.ui import WebDriverWait

            # 等待DOM加载完成
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # 额外等待JavaScript执行完成
            try:
                driver.execute_script(
                    "return jQuery.active == 0"
                    if "jQuery" in driver.execute_script("return typeof jQuery")
                    else "return true"
                )
            except Exception:
                pass  # jQuery可能不存在

            if logger:
                logger.debug("页面加载完成")

            return True

        except Exception as e:
            if logger:
                logger.debug(f"页面加载检查超时: {e}")
            return False

    @classmethod
    def smart_page_wait(
        cls,
        driver,
        expected_elements: Optional[list] = None,
        logger: Optional[logging.Logger] = None,
    ) -> bool:
        """
        智能页面等待，等待关键元素出现而不是固定时间

        Args:
            driver: WebDriver实例
            expected_elements: 期望的关键元素选择器列表
            logger: 日志器

        Returns:
            是否等待成功
        """
        try:
            # 先等待基本页面加载
            if cls.wait_for_page_ready(driver, 5, logger):
                # 如果指定了关键元素，等待它们出现
                if expected_elements:
                    from selenium.webdriver.support import expected_conditions as EC
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.common.by import By

                    for selector in expected_elements[:3]:  # 最多检查前3个元素
                        try:
                            WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, selector)
                                )
                            )
                            if logger:
                                logger.debug(f"关键元素已加载: {selector}")
                            break
                        except Exception:
                            continue

                # 最后一个短暂的缓冲延迟
                cls.smart_wait(cls.CLICK_DELAY, 0.5, logger)
                return True
            else:
                # 回退到固定延迟
                cls.smart_wait(cls.PAGE_LOAD_DELAY, 1.0, logger)
                return False

        except Exception as e:
            if logger:
                logger.debug(f"智能页面等待失败: {e}")
            # 回退到固定延迟
            cls.smart_wait(cls.PAGE_LOAD_DELAY, 1.0, logger)
            return False
