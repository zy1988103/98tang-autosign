"""
浏览器辅助工具模块

提供点击、滚动等浏览器操作的辅助功能
"""

import time
import random
import logging
from typing import Optional

from ..utils.timing import TimingManager


class BrowserHelper:
    """浏览器辅助工具"""

    @staticmethod
    def safe_click(driver, element, logger: Optional[logging.Logger] = None) -> None:
        """
        安全点击元素

        Args:
            driver: WebDriver实例
            element: 要点击的元素
            logger: 日志器
        """
        try:
            # 滚动到元素位置
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                element,
            )
            TimingManager.smart_wait(TimingManager.CLICK_DELAY, 0.8, logger)

            # 优先使用JavaScript点击，更快更可靠
            driver.execute_script("arguments[0].click();", element)

        except Exception as e:
            if logger:
                logger.debug(f"JavaScript点击失败，使用原生点击: {e}")
            try:
                element.click()
            except Exception as e2:
                if logger:
                    logger.warning(f"元素点击失败: {e2}")
                raise

    @staticmethod
    def random_wait(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
        """
        随机等待（向后兼容）

        Args:
            min_seconds: 最小等待时间
            max_seconds: 最大等待时间
        """
        wait_time = random.uniform(min_seconds, max_seconds)
        time.sleep(wait_time)

    @staticmethod
    def random_scroll(driver, logger: Optional[logging.Logger] = None) -> None:
        """
        随机滚动页面

        Args:
            driver: WebDriver实例
            logger: 日志器
        """
        try:
            scroll_count = random.randint(2, 4)
            for i in range(scroll_count):
                # 检查是否到底部
                at_bottom = driver.execute_script(
                    "return (window.innerHeight + window.pageYOffset) >= document.body.offsetHeight - 10;"
                )
                if at_bottom:
                    break

                scroll_distance = random.randint(200, 600)
                driver.execute_script(
                    f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});"
                )

                # 根据滚动进度调整等待时间
                progress_multiplier = 1.0 - (i / scroll_count) * 0.3
                TimingManager.smart_wait(
                    TimingManager.SCROLL_DELAY, progress_multiplier, logger
                )

        except Exception as e:
            if logger:
                logger.warning(f"随机滚动失败: {e}")

    @staticmethod
    def human_like_scroll(driver, logger: Optional[logging.Logger] = None) -> None:
        """
        人性化滚动，使用平滑的smooth行为模拟真实用户

        Args:
            driver: WebDriver实例
            logger: 日志器
        """
        try:
            # 获取页面信息
            page_info = driver.execute_script(
                """
                return {
                    totalHeight: Math.max(
                        document.body.scrollHeight,
                        document.body.offsetHeight,
                        document.documentElement.clientHeight,
                        document.documentElement.scrollHeight,
                        document.documentElement.offsetHeight
                    ),
                    viewHeight: window.innerHeight,
                    currentPos: window.pageYOffset
                };
            """
            )

            total_height = page_info["totalHeight"]
            view_height = page_info["viewHeight"]
            current_pos = page_info["currentPos"]

            if logger:
                logger.debug(
                    f"页面滚动信息: 总高度={total_height}, 视窗高度={view_height}, 当前位置={current_pos}"
                )

            # 如果页面太短，不需要滚动
            if total_height <= view_height + 100:
                if logger:
                    logger.debug("页面内容较短，无需滚动")
                return

            # 模拟人类真实的滚动行为模式
            scroll_behaviors = [
                {
                    "name": "初始扫视",
                    "target_percent": 0.15,
                    "scroll_type": "fast_preview",
                },
                {
                    "name": "仔细阅读",
                    "target_percent": 0.4,
                    "scroll_type": "careful_reading",
                },
                {
                    "name": "快速浏览",
                    "target_percent": 0.7,
                    "scroll_type": "quick_browse",
                },
                {
                    "name": "到达底部",
                    "target_percent": 0.95,
                    "scroll_type": "final_scroll",
                },
            ]

            max_scroll_position = total_height - view_height

            for behavior in scroll_behaviors:
                target_position = int(max_scroll_position * behavior["target_percent"])
                current_position = driver.execute_script("return window.pageYOffset;")

                # 如果已经超过目标位置，跳过
                if current_position >= target_position:
                    continue

                if logger:
                    logger.debug(
                        f"执行滚动行为: {behavior['name']} (目标位置: {target_position}px)"
                    )

                # 使用smooth滚动到目标位置
                driver.execute_script(
                    f"""
                    window.scrollTo({{
                        top: {target_position},
                        behavior: 'smooth'
                    }});
                """
                )

                # 使用智能延迟管理器，根据滚动类型调整等待时间
                if behavior["scroll_type"] == "fast_preview":
                    TimingManager.smart_wait(TimingManager.READING_DELAY, 0.6, logger)
                elif behavior["scroll_type"] == "careful_reading":
                    TimingManager.smart_wait(TimingManager.READING_DELAY, 1.4, logger)
                    # 在阅读过程中偶尔小幅滚动
                    if random.random() < 0.6:
                        small_adjustment = random.randint(-50, 100)
                        driver.execute_script(
                            f"""
                            window.scrollBy({{
                                top: {small_adjustment},
                                behavior: 'smooth'
                            }});
                        """
                        )
                        TimingManager.smart_wait(
                            TimingManager.SCROLL_DELAY, 0.5, logger
                        )
                elif behavior["scroll_type"] == "quick_browse":
                    TimingManager.smart_wait(TimingManager.READING_DELAY, 1.0, logger)
                else:  # final_scroll
                    TimingManager.smart_wait(TimingManager.SCROLL_DELAY, 0.8, logger)

                # 检查是否需要提前结束（页面动态加载内容导致高度变化）
                new_total_height = driver.execute_script(
                    "return document.body.scrollHeight;"
                )
                if new_total_height != total_height:
                    if logger:
                        logger.debug(
                            f"页面高度发生变化: {total_height} -> {new_total_height}"
                        )
                    total_height = new_total_height
                    max_scroll_position = total_height - view_height

            if logger:
                logger.debug("人性化平滑滚动完成")

        except Exception as e:
            if logger:
                logger.warning(f"人性化滚动失败: {e}")
            # 回退到简单滚动
            BrowserHelper.random_scroll(driver, logger)

    @staticmethod
    def scroll_to_element(
        driver, element, logger: Optional[logging.Logger] = None
    ) -> None:
        """
        滚动到指定元素

        Args:
            driver: WebDriver实例
            element: 目标元素
            logger: 日志器
        """
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                element,
            )
            TimingManager.smart_wait(TimingManager.SCROLL_DELAY, 0.5, logger)
        except Exception as e:
            if logger:
                logger.warning(f"滚动到元素失败: {e}")

    @staticmethod
    def scroll_to_bottom(driver, logger: Optional[logging.Logger] = None) -> None:
        """
        滚动到页面底部

        Args:
            driver: WebDriver实例
            logger: 日志器
        """
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            TimingManager.smart_wait(TimingManager.SCROLL_DELAY, 1.0, logger)
        except Exception as e:
            if logger:
                logger.warning(f"滚动到底部失败: {e}")

    @staticmethod
    def get_page_info(driver) -> dict:
        """
        获取页面信息

        Args:
            driver: WebDriver实例

        Returns:
            页面信息字典
        """
        try:
            return driver.execute_script(
                """
                return {
                    url: window.location.href,
                    title: document.title,
                    scrollY: window.pageYOffset,
                    scrollHeight: document.body.scrollHeight,
                    viewHeight: window.innerHeight,
                    viewWidth: window.innerWidth
                };
                """
            )
        except Exception:
            return {
                "url": "",
                "title": "",
                "scrollY": 0,
                "scrollHeight": 0,
                "viewHeight": 0,
                "viewWidth": 0,
            }
