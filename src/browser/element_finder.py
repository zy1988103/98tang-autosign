"""
元素查找模块

提供页面元素定位和查找功能
"""

import logging
from typing import List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class ElementFinder:
    """元素查找器"""

    def __init__(self, driver, logger: Optional[logging.Logger] = None):
        """
        初始化元素查找器

        Args:
            driver: WebDriver实例
            logger: 日志器
        """
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)

    def find_by_selectors(self, selectors: List[str], timeout: int = 5) -> Optional:
        """
        通过多个选择器查找元素

        Args:
            selectors: 选择器列表
            timeout: 超时时间

        Returns:
            找到的元素或None
        """
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )

                if element and element.is_displayed():
                    self.logger.debug(f"找到元素: {selector}")
                    return element

            except (TimeoutException, NoSuchElementException):
                continue

        self.logger.debug(f"未找到任何元素: {selectors}")
        return None

    def find_clickable_by_selectors(
        self, selectors: List[str], timeout: int = 5
    ) -> Optional:
        """
        通过多个选择器查找可点击元素

        Args:
            selectors: 选择器列表
            timeout: 超时时间

        Returns:
            找到的可点击元素或None
        """
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )

                self.logger.debug(f"找到可点击元素: {selector}")
                return element

            except (TimeoutException, NoSuchElementException):
                continue

        self.logger.debug(f"未找到任何可点击元素: {selectors}")
        return None

    def find_elements_by_selectors(self, selectors: List[str]) -> List:
        """
        通过多个选择器查找多个元素

        Args:
            selectors: 选择器列表

        Returns:
            找到的元素列表
        """
        elements = []
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    found_elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    found_elements = self.driver.find_elements(
                        By.CSS_SELECTOR, selector
                    )

                # 只添加可见的元素
                visible_elements = [
                    elem for elem in found_elements if elem.is_displayed()
                ]
                elements.extend(visible_elements)

                if visible_elements:
                    self.logger.debug(
                        f"找到 {len(visible_elements)} 个元素: {selector}"
                    )

            except Exception as e:
                self.logger.debug(f"查找元素失败 {selector}: {e}")
                continue

        return elements

    def wait_for_element_disappear(self, selector: str, timeout: int = 10) -> bool:
        """
        等待元素消失

        Args:
            selector: 元素选择器
            timeout: 超时时间

        Returns:
            元素是否消失
        """
        try:
            if selector.startswith("//"):
                WebDriverWait(self.driver, timeout).until_not(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
            else:
                WebDriverWait(self.driver, timeout).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            return True
        except TimeoutException:
            return False

    def is_element_present(self, selector: str) -> bool:
        """
        检查元素是否存在

        Args:
            selector: 元素选择器

        Returns:
            元素是否存在
        """
        try:
            if selector.startswith("//"):
                elements = self.driver.find_elements(By.XPATH, selector)
            else:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return len(elements) > 0
        except Exception:
            return False

    def get_element_text(self, selector: str) -> Optional[str]:
        """
        获取元素文本

        Args:
            selector: 元素选择器

        Returns:
            元素文本或None
        """
        element = self.find_by_selectors([selector])
        if element:
            return element.text.strip()
        return None
