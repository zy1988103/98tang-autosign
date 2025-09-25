"""
拟人化行为模块

提供随机浏览和回帖等拟人化操作
"""

import random
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin

from ..browser.helpers import BrowserHelper
from ..browser.element_finder import ElementFinder
from ..utils.timing import TimingManager


class HumanlikeBehavior:
    """拟人化行为管理器"""

    def __init__(self, driver, config: Dict, logger: Optional[logging.Logger] = None):
        """
        初始化拟人化行为管理器

        Args:
            driver: WebDriver实例
            config: 配置字典
            logger: 日志器
        """
        self.driver = driver
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.element_finder = ElementFinder(driver, logger)

        self.base_url = config.get("base_url", "https://www.sehuatang.org")
        self.reply_messages = config.get("reply_messages", [])
        self.comment_interval = config.get("comment_interval", 15)

        # 设置评论间隔
        TimingManager.set_comment_interval(self.comment_interval)

    def random_browse_pages(self, page_count: int = 3) -> None:
        """
        执行随机浏览行为

        Args:
            page_count: 要浏览的页数
        """
        try:
            self.logger.info(f"开始浏览综合讨论区，共 {page_count} 页")

            # 综合讨论区
            section = {
                "name": "综合讨论区",
                "fid": 95,
                "url": f"{self.base_url}/forum.php?mod=forumdisplay&fid=95",
            }

            try:
                # 访问版块首页
                self.driver.get(section["url"])
                TimingManager.smart_wait(
                    TimingManager.PAGE_LOAD_DELAY, 1.0, self.logger
                )

                self.logger.info(f"计划在 {section['name']} 中浏览 {page_count} 页")

                for page_num in range(page_count):
                    try:
                        current_page = page_num + 1
                        self.logger.info(
                            f"正在浏览 {section['name']} 第 {current_page} 页"
                        )

                        # 模拟真实用户的滚动行为
                        BrowserHelper.human_like_scroll(self.driver, self.logger)

                        # 如果不是最后一页，尝试翻页
                        if page_num < page_count - 1:
                            TimingManager.smart_wait(
                                TimingManager.NAVIGATION_DELAY, 1.0, self.logger
                            )
                            success = self._browse_next_page_with_click()
                            if not success:
                                self.logger.info(
                                    f"{section['name']} 无法继续翻页，结束浏览"
                                )
                                break
                        else:
                            # 最后一页时，稍微停留观察
                            if page_num == 0:
                                TimingManager.adaptive_wait(
                                    TimingManager.PAGE_LOAD_DELAY,
                                    "complex",
                                    self.logger,
                                )
                            else:
                                TimingManager.smart_wait(
                                    TimingManager.READING_DELAY, 1.2, self.logger
                                )

                    except Exception as e:
                        self.logger.warning(
                            f"浏览 {section['name']} 第 {current_page} 页失败: {e}"
                        )
                        break

            except Exception as e:
                self.logger.warning(f"浏览版块 {section['name']} 失败: {e}")

            self.logger.info("随机浏览完成")

        except Exception as e:
            self.logger.warning(f"随机浏览失败: {e}")

    def find_reply_targets(self, reply_count: int = 2) -> List[Dict]:
        """
        查找回帖目标，从第二页开始查找

        Args:
            reply_count: 需要的回帖数量

        Returns:
            回帖目标列表
        """
        try:
            # 先访问第一页
            discussion_url = f"{self.base_url}/forum.php?mod=forumdisplay&fid=95"
            self.driver.get(discussion_url)
            TimingManager.smart_wait(TimingManager.PAGE_LOAD_DELAY, 1.0, self.logger)

            self.logger.info("开始从第二页查找可回复的帖子")

            # 尝试翻页到第二页
            next_button = self._find_visible_next_page_button()
            if next_button:
                self.logger.info("找到下一页按钮，正在翻页到第二页")
                if self._click_next_page_button(next_button):
                    self.logger.info("翻页成功")
                else:
                    self.logger.debug("翻页失败，尝试直接访问第二页")
                    page2_url = (
                        f"{self.base_url}/forum.php?mod=forumdisplay&fid=95&page=2"
                    )
                    self.driver.get(page2_url)
                    TimingManager.smart_wait(
                        TimingManager.PAGE_LOAD_DELAY, 1.0, self.logger
                    )
            else:
                self.logger.warning("未找到下一页按钮，尝试直接访问第二页")
                page2_url = f"{self.base_url}/forum.php?mod=forumdisplay&fid=95&page=2"
                self.driver.get(page2_url)
                TimingManager.smart_wait(
                    TimingManager.PAGE_LOAD_DELAY, 1.0, self.logger
                )

            # 在第二页查找帖子
            post_links = []
            selectors = [
                "tbody[id^='normalthread'] a.xst",
                "a.xst",
                "th a[href*='thread-']",
            ]

            for selector in selectors:
                try:
                    from selenium.webdriver.common.by import By

                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    # 从第二页的前20个帖子中选择
                    for element in elements[:20]:
                        href = element.get_attribute("href")
                        title = element.text.strip()

                        if href and title and len(title) > 4:
                            post_links.append(
                                {
                                    "url": urljoin(self.base_url, href),
                                    "title": title[:50],
                                }
                            )

                    if post_links:
                        break
                except Exception:
                    continue

            # 去重并随机选择
            unique_posts = []
            seen_urls = set()
            for post in post_links:
                if post["url"] not in seen_urls:
                    unique_posts.append(post)
                    seen_urls.add(post["url"])

            random.shuffle(unique_posts)
            selected_posts = unique_posts[:reply_count]

            self.logger.info(
                f"从第二页找到 {len(unique_posts)} 个可回复帖子，选择 {len(selected_posts)} 个进行回复"
            )

            return selected_posts

        except Exception as e:
            self.logger.error(f"查找回帖目标失败: {e}")
            return []

    def reply_to_post(self, post_info: Dict) -> bool:
        """
        回复帖子

        Args:
            post_info: 帖子信息字典

        Returns:
            是否回复成功
        """
        try:
            self.logger.info(f"回复帖子: {post_info['title']}")

            self.driver.get(post_info["url"])
            TimingManager.smart_wait(TimingManager.PAGE_LOAD_DELAY, 1.0, self.logger)

            # 模拟用户阅读帖子内容
            BrowserHelper.human_like_scroll(self.driver, self.logger)

            # 智能滚动到回复区域
            reply_textarea = self._smart_scroll_to_reply_area()
            if not reply_textarea:
                self.logger.warning("未找到回复文本框")
                return False

            # 填写回复内容
            reply_text = random.choice(self.reply_messages)
            reply_textarea.clear()
            reply_textarea.send_keys(reply_text)
            TimingManager.smart_wait(TimingManager.NAVIGATION_DELAY, 1.0, self.logger)

            # 提交回复
            submit_selectors = [
                "#fastpostsubmit",
                "input[name='replysubmit']",
                "button[type='submit']",
            ]

            submit_button = self.element_finder.find_clickable_by_selectors(
                submit_selectors
            )
            if submit_button:
                BrowserHelper.safe_click(self.driver, submit_button, self.logger)
                TimingManager.smart_wait(
                    TimingManager.PAGE_LOAD_DELAY, 1.0, self.logger
                )
                self.logger.info("回复提交成功")
                return True
            else:
                self.logger.warning("未找到提交按钮")
                return False

        except Exception as e:
            self.logger.error(f"回复帖子失败: {e}")
            return False

    def perform_humanlike_activities(self) -> None:
        """执行拟人化活动"""
        try:
            self.logger.info("开始拟人化活动")
            TimingManager.adaptive_wait(
                TimingManager.PAGE_LOAD_DELAY, "normal", self.logger
            )

            # 随机浏览
            if self.config.get("enable_random_browsing", False):
                self.logger.info("执行随机浏览")
                page_count = self.config.get("browse_page_count", 3)
                self.random_browse_pages(page_count)

            # 回帖活动
            if self.config.get("enable_reply", False):
                reply_count = self.config.get("reply_count", 2)
                self.logger.info(f"开始回帖活动，目标数量: {reply_count}")
                post_targets = self.find_reply_targets(reply_count)

                success_count = 0
                for i, post_info in enumerate(post_targets):
                    if self.reply_to_post(post_info):
                        success_count += 1

                    # 两次回帖间隔
                    if i < len(post_targets) - 1:
                        wait_time = TimingManager.smart_wait(
                            TimingManager.REPLY_INTERVAL_DELAY, 1.0, self.logger
                        )
                        self.logger.info(
                            f"回帖间隔等待 {wait_time:.1f} 秒，模拟真实用户行为"
                        )

                self.logger.info(
                    f"回帖活动完成，成功 {success_count}/{len(post_targets)} 个"
                )

        except Exception as e:
            self.logger.warning(f"拟人化活动失败: {e}")

    def _smart_scroll_to_reply_area(self):
        """智能滚动到回复区域，检测是否到达底部"""
        try:
            self.logger.info("寻找回复文本框")

            # 回复文本框选择器
            reply_selectors = [
                "#fastpostmessage",
                "textarea[name='message']",
                "#e_textarea",
                "textarea[id*='post']",
                "textarea[class*='reply']",
            ]

            # 首先尝试在当前视窗中查找
            reply_textarea = self.element_finder.find_by_selectors(reply_selectors, 2)
            if reply_textarea and reply_textarea.is_displayed():
                self.logger.info("在当前视窗中找到回复文本框")
                return reply_textarea

            # 如果没找到，滚动到底部寻找
            BrowserHelper.scroll_to_bottom(self.driver, self.logger)

            # 再次查找
            reply_textarea = self.element_finder.find_by_selectors(reply_selectors, 3)
            if reply_textarea:
                self.logger.info("在页面底部找到回复文本框")
                BrowserHelper.scroll_to_element(
                    self.driver, reply_textarea, self.logger
                )
                return reply_textarea

            self.logger.warning("未找到回复文本框")
            return None

        except Exception as e:
            self.logger.warning(f"智能滚动到回复区域失败: {e}")
            return None

    def _find_visible_next_page_button(self):
        """查找可见的下一页按钮"""
        next_page_selectors = [
            "#fd_page_bottom .pg a.nxt",
            "#fd_page_top .pg a.nxt",
            "a.nxt",
            "a[title*='下一页']",
            "//a[contains(text(), '下一页')]",
        ]

        return self.element_finder.find_clickable_by_selectors(next_page_selectors, 2)

    def _click_next_page_button(self, element) -> bool:
        """点击下一页按钮"""
        try:
            element_text = element.text.strip()
            href = element.get_attribute("href")

            self.logger.info(f"准备点击下一页按钮: {element_text} - {href}")

            BrowserHelper.safe_click(self.driver, element, self.logger)
            TimingManager.smart_wait(TimingManager.PAGE_LOAD_DELAY, 1.0, self.logger)

            # 验证翻页是否成功
            new_url = self.driver.current_url
            if "page=" in new_url:
                self.logger.info(f"翻页成功，当前URL: {new_url}")
                return True
            else:
                self.logger.debug("翻页后URL未变化")
                return False

        except Exception as e:
            self.logger.debug(f"点击下一页按钮失败: {e}")
            return False

    def _browse_next_page_with_click(self) -> bool:
        """专门用于浏览时的真实翻页点击"""
        try:
            next_button = self._find_visible_next_page_button()

            if next_button:
                self.logger.info("找到合适的翻页按钮，准备点击")
                return self._click_next_page_button(next_button)

            self.logger.debug("未找到任何可用的翻页按钮")
            return False

        except Exception as e:
            self.logger.debug(f"浏览翻页失败: {e}")
            return False
