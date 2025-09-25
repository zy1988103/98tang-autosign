"""
签到核心模块

提供网站登录和签到的核心功能
"""

import re
import logging
from typing import Optional, Dict, Any

from ..browser.helpers import BrowserHelper
from ..browser.element_finder import ElementFinder
from ..utils.timing import TimingManager


class SignInManager:
    """签到管理器"""

    def __init__(
        self, driver, config: Dict[str, Any], logger: Optional[logging.Logger] = None
    ):
        """
        初始化签到管理器

        Args:
            driver: WebDriver实例
            config: 配置字典
            logger: 日志器
        """
        self.driver = driver
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.element_finder = ElementFinder(driver, logger)

        # 网站配置
        self.base_url = config.get("base_url", "https://www.sehuatang.org")
        self.home_url = self.base_url
        self.sign_url = f"{self.base_url}/plugin.php?id=dsu_paulsign:sign"

        # 认证配置
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        self.enable_security_question = config.get("enable_security_question", False)
        self.security_answer = config.get("security_answer", "")
        self.security_question = config.get("security_question", "")

    def handle_age_verification(self) -> bool:
        """
        处理年龄验证

        Returns:
            是否处理成功
        """
        try:
            self.logger.debug("开始检查年龄验证页面")

            age_selectors = [
                "a[href*='agecheck']",
                "//a[contains(text(), '满18岁')]",
                "//a[contains(text(), '请点此进入')]",
            ]

            age_link = self.element_finder.find_by_selectors(age_selectors, timeout=3)
            if age_link:
                self.logger.info("检测到年龄验证页面，正在处理")
                link_text = age_link.text
                link_href = age_link.get_attribute("href")
                self.logger.debug(
                    f"找到年龄验证链接 - 文本: '{link_text}', href: '{link_href}'"
                )

                BrowserHelper.safe_click(self.driver, age_link, self.logger)
                TimingManager.smart_page_wait(
                    self.driver, ["#main", ".wp", "body"], self.logger
                )

                self.logger.info("年龄验证处理完成")
                return True

            self.logger.debug("未检测到年龄验证页面，无需处理")
            return True  # 无需验证

        except Exception as e:
            self.logger.warning(f"年龄验证处理失败: {e}")
            return True  # 继续执行

    def check_login_status(self) -> bool:
        """
        检查登录状态

        Returns:
            是否已登录
        """
        try:
            self.logger.debug("开始检查登录状态")

            # 首先检查是否有登录错误消息
            error_message = self.check_login_error_message()
            if error_message:
                self.logger.error(f"登录失败，错误信息: {error_message}")
                return False

            username_selectors = [
                f"//strong[contains(text(), '{self.username}')]",
                f"//a[contains(text(), '{self.username}')]",
                ".vwmy strong",
                "//div[@class='vwmy']//strong",
            ]

            username_element = self.element_finder.find_by_selectors(
                username_selectors, timeout=3
            )

            if username_element:
                element_text = username_element.text
                self.logger.debug(f"找到用户名元素，文本内容: '{element_text}'")
                if self.username in element_text:
                    self.logger.debug("用户名匹配成功，已登录")
                    return True
                else:
                    self.logger.debug(
                        f"用户名不匹配，期望: '{self.username}', 实际: '{element_text}'"
                    )

            # 检查其他登录指示器
            login_indicators = [
                "//a[contains(@href, 'logging.php?action=logout')]",
                "//a[contains(text(), '退出')]",
                ".vwmy",
            ]

            indicator = self.element_finder.find_by_selectors(
                login_indicators, timeout=3
            )

            if indicator:
                self.logger.debug("找到登录指示器")
                return True

            self.logger.debug("未找到任何登录指示器")
            return False

        except Exception as e:
            self.logger.warning(f"检查登录状态失败: {e}")
            return False

    def check_login_error_message(self) -> Optional[str]:
        """
        检查登录错误消息

        Returns:
            错误消息文本，如果没有错误则返回None
        """
        try:
            # 检查页面源代码中的JavaScript错误处理
            page_source = self.driver.page_source

            # 检查密码错误次数过多的提示
            if "密码错误次数过多" in page_source:
                import re

                # 提取具体的错误消息
                error_pattern = r"errorhandle_login\('([^']+)'"
                match = re.search(error_pattern, page_source)
                if match:
                    error_msg = match.group(1)
                    self.logger.warning(f"检测到账号锁定: {error_msg}")
                    return error_msg
                return "密码错误次数过多，账号已被临时锁定"

            # 检查其他常见的登录错误消息
            error_indicators = [
                "用户名或密码错误",
                "账号已被禁用",
                "验证码错误",
                "安全提问答案错误",
                "登录失败",
                "请重新登录",
            ]

            for error_text in error_indicators:
                if error_text in page_source:
                    return error_text

            # 检查弹窗中的错误消息
            error_selectors = [
                "#ntcwin .pc_inner i",  # 错误弹窗
                "#returnmessage_Luu4S",  # 登录返回消息
                ".alert_error",  # 错误提示
                ".error",  # 通用错误
            ]

            for selector in error_selectors:
                try:
                    error_element = self.element_finder.find_by_selectors(
                        [selector], timeout=1
                    )
                    if error_element and error_element.text.strip():
                        error_text = error_element.text.strip()
                        if any(
                            keyword in error_text
                            for keyword in ["错误", "失败", "禁用"]
                        ):
                            return error_text
                except:
                    continue

            return None

        except Exception as e:
            self.logger.debug(f"检查登录错误消息时出错: {e}")
            return None

    def fill_login_form(self) -> bool:
        """
        填写登录表单

        Returns:
            是否填写成功
        """
        try:
            self.logger.debug("开始填写登录表单")

            # 用户名输入框
            username_selectors = [
                "#fwin_login input[name='username']",
                "#username",
                "input[name='username']",
            ]

            username_input = self.element_finder.find_by_selectors(username_selectors)
            if not username_input:
                self.logger.error("未找到用户名输入框")
                return False

            self.logger.debug("找到用户名输入框，开始填写")
            username_input.clear()
            username_input.send_keys(self.username)
            self.logger.debug(
                f"用户名已填写: {self.username[:2]}{'*' * (len(self.username) - 2) if len(self.username) > 2 else '***'}"
            )

            # 密码输入框
            password_selectors = [
                "#fwin_login input[name='password']",
                "#password",
                "input[name='password']",
            ]

            password_input = self.element_finder.find_by_selectors(password_selectors)
            if not password_input:
                self.logger.error("未找到密码输入框")
                return False

            self.logger.debug("找到密码输入框，开始填写")
            password_input.clear()
            password_input.send_keys(self.password)
            self.logger.debug("密码已填写（已掩码）")

            TimingManager.smart_wait(TimingManager.NAVIGATION_DELAY, 1.0, self.logger)
            self.logger.debug("登录表单填写完成")
            return True

        except Exception as e:
            self.logger.error(f"填写登录表单失败: {e}")
            return False

    def handle_security_question(self) -> bool:
        """
        处理安全提问

        Returns:
            是否处理成功
        """
        if not self.enable_security_question:
            return True

        try:
            question_select = self.element_finder.find_by_selectors(
                ["select[name='questionid']", "#questionid"]
            )

            if not question_select:
                return True  # 无安全提问

            self.logger.info("处理安全提问")

            # 选择安全问题
            from selenium.webdriver.common.by import By

            options = question_select.find_elements(By.TAG_NAME, "option")
            for option in options:
                if self.security_question in option.text:
                    option.click()
                    break

            # 填写答案
            answer_input = self.element_finder.find_by_selectors(
                ["input[name='answer']", "#answer"]
            )

            if answer_input:
                answer_input.clear()
                answer_input.send_keys(self.security_answer)
                self.logger.debug("安全提问答案已填写（已掩码）")
                return True

            return False

        except Exception as e:
            self.logger.error(f"处理安全提问失败: {e}")
            return False

    def login(self) -> bool:
        """
        登录网站

        Returns:
            是否登录成功
        """
        try:
            self.logger.info("开始登录流程")

            # 访问首页
            self.logger.debug(f"访问首页: {self.home_url}")
            self.driver.get(self.home_url)
            TimingManager.smart_wait(TimingManager.PAGE_LOAD_DELAY, 1.0, self.logger)

            # 处理年龄验证
            self.logger.debug("开始处理年龄验证")
            if not self.handle_age_verification():
                self.logger.debug("年龄验证处理失败")
                return False

            # 查找并点击登录按钮
            login_selectors = [
                "//button[@type='submit']//em[contains(text(), '登录')]/..",
                "//button[contains(text(), '登录')]",
                "#loginsubmit",
            ]

            login_button = self.element_finder.find_clickable_by_selectors(
                login_selectors
            )
            if not login_button:
                self.logger.error("未找到登录按钮")
                return False

            button_text = login_button.text
            self.logger.debug(f"找到登录按钮，文本: '{button_text}'，准备点击")
            BrowserHelper.safe_click(self.driver, login_button, self.logger)
            TimingManager.smart_wait(TimingManager.NAVIGATION_DELAY, 1.0, self.logger)

            # 等待登录弹窗
            self.logger.debug("等待登录弹窗出现")
            login_popup = self.element_finder.find_by_selectors(
                ["#fwin_login"], timeout=5
            )
            if not login_popup:
                self.logger.warning("未检测到登录弹窗")
            else:
                self.logger.debug("登录弹窗已出现")

            # 填写登录表单
            self.logger.debug("开始填写登录表单")
            if not self.fill_login_form():
                self.logger.debug("登录表单填写失败")
                return False

            # 处理安全提问
            self.logger.debug("处理安全提问")
            if not self.handle_security_question():
                self.logger.warning("安全提问处理失败，继续尝试")

            # 提交登录
            submit_selectors = [
                "#fwin_login button[type='submit']",
                "button[type='submit']",
                "#loginsubmit",
            ]

            submit_button = self.element_finder.find_clickable_by_selectors(
                submit_selectors
            )
            if not submit_button:
                self.logger.error("未找到提交按钮")
                return False

            submit_text = submit_button.text
            self.logger.debug(f"找到提交按钮，文本: '{submit_text}'，准备提交登录")
            BrowserHelper.safe_click(self.driver, submit_button, self.logger)
            TimingManager.adaptive_wait(
                TimingManager.PAGE_LOAD_DELAY, "complex", self.logger
            )

            # 验证登录结果
            self.logger.debug("验证登录结果")
            login_result = self.check_login_status()
            if login_result:
                self.logger.info("登录成功")
                return True
            else:
                # 检查是否是账号锁定
                error_message = self.check_login_error_message()
                if error_message and "密码错误次数过多" in error_message:
                    self.logger.error(f"账号被锁定: {error_message}")
                    # 如果是账号锁定，不要继续重试，直接返回失败
                    raise Exception(f"账号锁定: {error_message}")
                else:
                    self.logger.warning("登录失败")
                    return False

        except Exception as e:
            self.logger.error(f"登录过程出错: {e}")
            return False

    def calculate_math_answer(self, question: str) -> Optional[int]:
        """
        计算数学问题答案

        Args:
            question: 数学问题字符串

        Returns:
            计算结果或None
        """
        try:
            pattern = r"(\d+)\s*([+\-*/])\s*(\d+)"
            match = re.search(pattern, question)

            if not match:
                return None

            num1 = int(match.group(1))
            operator = match.group(2)
            num2 = int(match.group(3))

            operations = {
                "+": lambda x, y: x + y,
                "-": lambda x, y: x - y,
                "*": lambda x, y: x * y,
                "/": lambda x, y: x // y,
            }

            if operator in operations:
                return operations[operator](num1, num2)

            return None

        except Exception:
            return None

    def handle_sign_verification(self) -> bool:
        """
        处理签到验证

        Returns:
            是否处理成功
        """
        try:
            self.logger.debug("开始处理签到验证")
            TimingManager.smart_wait(TimingManager.NAVIGATION_DELAY, 1.0, self.logger)

            # 查找数学问题
            self.logger.debug("查找页面中的数学验证问题")
            question_text = self.driver.execute_script(
                """
                var allText = document.body.innerText;
                var mathPattern = /(\\d+)\\s*[+\\-*/]\\s*(\\d+)\\s*=\\s*\\?/;
                var match = allText.match(mathPattern);
                return match ? match[0] : '';
            """
            )

            if not question_text:
                self.logger.info("未发现验证问题，尝试直接提交")
                return True

            self.logger.info(f"处理验证问题: {question_text}")
            self.logger.debug(f"检测到数学验证问题: {question_text}")

            answer = self.calculate_math_answer(question_text)

            if answer is None:
                self.logger.error("无法计算答案")
                return False

            self.logger.debug(f"计算出答案: {answer}")

            # 填写答案
            answer_selectors = ['input[name="secanswer"]', 'input[id*="secqaaverify"]']

            answer_input = self.element_finder.find_by_selectors(answer_selectors)

            if answer_input:
                input_name = answer_input.get_attribute("name")
                input_id = answer_input.get_attribute("id")
                self.logger.debug(
                    f"找到答案输入框 - name: '{input_name}', id: '{input_id}'"
                )

                answer_input.clear()
                answer_input.send_keys(str(answer))
                self.logger.info(f"已填入答案: {answer}")
                self.logger.debug("答案填写完成")

                return True
            else:
                self.logger.error("未找到答案输入框")
                return False

        except Exception as e:
            self.logger.error(f"处理签到验证失败: {e}")
            return False

    def sign_in(self) -> bool:
        """
        执行签到

        Returns:
            是否签到成功
        """
        try:
            self.logger.info("开始签到流程")

            # 返回首页
            self.driver.get(self.home_url)
            TimingManager.smart_wait(TimingManager.PAGE_LOAD_DELAY, 1.0, self.logger)

            # 尝试进入签到页面，最多重试3次
            if not self._navigate_to_signin_page():
                self.logger.error("无法进入签到页面")
                return False

            # 检查签到状态
            signin_status = self._check_signin_status()

            if signin_status == "already_signed":
                self.logger.info("✅ 今日已签到")
                return True
            elif signin_status == "need_signin":
                self.logger.info("检测到未签到状态，开始执行签到")
                # 继续执行签到流程
            else:
                self.logger.error("无法确定签到状态")
                return False

            # 执行签到操作
            return self._perform_signin_action()

        except Exception as e:
            self.logger.error(f"签到失败: {e}")
            return False

    def _check_signin_status(self) -> str:
        """
        检查签到状态

        Returns:
            "already_signed": 已签到
            "need_signin": 需要签到
            "unknown": 无法确定状态
        """
        try:
            self.logger.debug("检查签到状态，查找签到按钮区域")

            # 先查找签到按钮区域
            sign_area_selector = "div.ddpc_sign_btna"
            sign_area = self.element_finder.find_by_selectors([sign_area_selector])

            if not sign_area:
                self.logger.warning("未找到签到按钮区域 div.ddpc_sign_btna")
                return "unknown"

            # 获取按钮区域的所有子元素
            buttons = sign_area.find_elements("tag name", "a")

            for button in buttons:
                try:
                    button_class = button.get_attribute("class") or ""
                    button_text = button.text.strip()

                    self.logger.debug(
                        f"检查按钮 - class: '{button_class}', text: '{button_text}'"
                    )

                    # 检查是否是灰色按钮（已签到）
                    if "ddpc_sign_btn_grey" in button_class:
                        if "今日已签到" in button_text:
                            self.logger.info(f"✅ 检测到已签到状态: {button_text}")
                            return "already_signed"

                    # 检查是否是红色按钮（未签到）
                    elif "ddpc_sign_btn_red" in button_class:
                        self.logger.info(f"🔴 检测到未签到状态: {button_text}")
                        return "need_signin"

                except Exception as e:
                    self.logger.debug(f"检查按钮时出错: {e}")
                    continue

            # 如果没有找到明确的按钮状态，返回未知状态
            self.logger.warning("⚠️ 未找到明确的签到按钮状态，返回未知状态")
            return "unknown"

        except Exception as e:
            self.logger.error(f"检查签到状态时出错: {e}")
            return "unknown"

    def _perform_signin_action(self) -> bool:
        """
        执行具体的签到操作

        Returns:
            是否签到成功
        """
        try:
            # 查找红色签到按钮
            sign_button_selectors = [
                "div.ddpc_sign_btna a.ddpc_sign_btn_red",
                "a.ddpc_sign_btn_red",
                'a[class*="sign_btn"]',
                'a[href*="sign"]',
            ]

            sign_button = self.element_finder.find_clickable_by_selectors(
                sign_button_selectors
            )
            if not sign_button:
                self.logger.error("未找到可点击的签到按钮")
                return False

            # 检查按钮文本和属性
            button_text = sign_button.text.strip()
            button_class = sign_button.get_attribute("class") or ""
            button_href = sign_button.get_attribute("href") or ""

            self.logger.debug(
                f"找到签到按钮 - 文本: '{button_text}', class: '{button_class}', href: '{button_href}'"
            )

            # 确保这是一个有效的签到按钮
            if "ddpc_sign_btn_red" in button_class or any(
                keyword in button_text for keyword in ["签到", "点击"]
            ):
                self.logger.info(f"开始点击签到按钮: '{button_text}'")
                BrowserHelper.safe_click(self.driver, sign_button, self.logger)
                TimingManager.smart_wait(
                    TimingManager.PAGE_LOAD_DELAY, 1.0, self.logger
                )

                # 处理签到验证
                if self.handle_sign_verification():
                    self.logger.info("✅ 签到成功完成")
                    return True
                else:
                    self.logger.error("❌ 签到验证失败")
                    return False
            else:
                self.logger.warning(f"按钮不符合签到条件: '{button_text}'")
                return False

        except Exception as e:
            self.logger.error(f"执行签到操作时出错: {e}")
            return False

    def _navigate_to_signin_page(self) -> bool:
        """
        导航到签到页面并验证URL

        Returns:
            是否成功进入签到页面
        """
        for attempt in range(3):
            try:
                self.logger.debug(f"尝试进入签到页面 - 第{attempt + 1}次")

                # 点击签到导航
                sign_nav_selectors = [
                    'a[href="plugin.php?id=dd_sign:index"]',
                    'a[href*="dd_sign"]',
                ]

                sign_nav_link = self.element_finder.find_clickable_by_selectors(
                    sign_nav_selectors
                )
                if not sign_nav_link:
                    self.logger.warning(f"第{attempt + 1}次未找到签到导航链接")
                    continue

                BrowserHelper.safe_click(self.driver, sign_nav_link, self.logger)
                TimingManager.smart_wait(
                    TimingManager.PAGE_LOAD_DELAY, 1.0, self.logger
                )

                # 验证当前URL是否为签到页面
                current_url = self.driver.current_url
                if "plugin.php?id=dd_sign" in current_url:
                    self.logger.info(f"成功进入签到页面: {current_url}")
                    return True
                else:
                    self.logger.warning(
                        f"第{attempt + 1}次未成功进入签到页面，当前URL: {current_url}"
                    )

            except Exception as e:
                self.logger.warning(f"第{attempt + 1}次进入签到页面失败: {e}")

        return False
