"""
主应用程序模块

整合所有功能模块，提供统一的签到服务
"""

import logging
import os
from typing import Optional
from datetime import datetime

from .config import ConfigManager
from .logger import LoggerManager
from ..browser.driver import BrowserDriverManager
from ..automation.signin import SignInManager
from ..automation.humanlike import HumanlikeBehavior
from ..utils.retry import RetryManager
from ..utils.timing import TimingManager
from ..notifications.telegram import (
    TelegramNotifier,
    TaskResult,
    ExecutionSummary,
)
from ..utils.timeout_protection import TimeoutProtectionContext


class AutoSignApp:
    """自动签到应用程序"""

    def __init__(self, config_file: str = "config.env", debug_mode: bool = False):
        """
        初始化应用程序

        Args:
            config_file: 配置文件路径
            debug_mode: 是否启用调试模式
        """
        self.debug_mode = debug_mode

        # 初始化配置管理器
        self.config_manager = ConfigManager(config_file)

        # 初始化日志管理器
        logging_config = self.config_manager.get_logging_config()
        self.logger_manager = LoggerManager()
        self.logger = self.logger_manager.setup_logger(
            name=__name__,
            log_level=logging_config["log_level"],
            log_dir=logging_config["log_dir"],
            max_log_files=logging_config["max_log_files"],
            debug_mode=debug_mode,
        )

        # 初始化其他组件
        self.browser_manager = BrowserDriverManager(self.logger)
        self.retry_manager = RetryManager(max_retries=3)

        # 业务逻辑管理器
        self.signin_manager: Optional[SignInManager] = None
        self.humanlike_manager: Optional[HumanlikeBehavior] = None

        # Telegram通知器
        self.telegram_notifier: Optional[TelegramNotifier] = None
        self._init_telegram_notifier()

        # 执行摘要数据
        self.execution_start_time: Optional[str] = None
        self.task_results: list = []

        # 应用全局延迟倍数
        timing_config = self.config_manager.get_timing_config()
        TimingManager.set_global_multiplier(timing_config["timing_multiplier"])
        TimingManager.set_comment_interval(timing_config["comment_interval"])

        if self.debug_mode:
            self.logger.info("调试模式已启用，将输出详细信息")

        # 使用安全配置显示，避免敏感信息泄露
        safe_config = self.config_manager.get_safe_config()
        self.logger.info(f"配置加载完成，用户名: {self.config_manager.get('username')}")
        self.logger.debug(f"安全配置: {safe_config}")

    def test_telegram_connection(self) -> bool:
        """
        测试Telegram连接

        Returns:
            是否连接成功
        """
        if not self.telegram_notifier:
            self.logger.error("Telegram通知器未初始化")
            return False

        try:
            return self.telegram_notifier.test_connection()
        except Exception as e:
            self.logger.error(f"Telegram连接测试失败: {e}")
            return False

    def _init_telegram_notifier(self) -> None:
        """初始化Telegram通知器"""
        try:
            # 检查是否启用Telegram通知
            if not self.config_manager.get("ENABLE_TELEGRAM_NOTIFICATION", False):
                self.logger.debug("Telegram通知未启用")
                return

            # 获取配置
            bot_token = self.config_manager.get("TELEGRAM_BOT_TOKEN", "").strip()
            chat_id = self.config_manager.get("TELEGRAM_CHAT_ID", "").strip()
            proxy_url = self.config_manager.get("TELEGRAM_PROXY_URL", "").strip()

            if not bot_token or not chat_id:
                self.logger.warning("Telegram通知已启用但配置不完整，跳过初始化")
                return

            # 创建通知器
            self.telegram_notifier = TelegramNotifier(
                bot_token=bot_token,
                chat_id=chat_id,
                proxy_url=proxy_url,
                logger=self.logger,
            )

            self.logger.info("Telegram通知器初始化成功")

        except Exception as e:
            self.logger.error(f"Telegram通知器初始化失败: {e}")
            self.telegram_notifier = None

    def _record_task_result(
        self, task_type: str, success: bool, message: str, details: str = None
    ) -> None:
        """记录任务执行结果"""
        task_result = TaskResult(
            task_type=task_type, success=success, message=message, details=details
        )
        self.task_results.append(task_result)

        # 不再发送单个任务通知，只在最后发送摘要

    def _send_error_with_log(self, error_message: str, error_title: str) -> None:
        """发送错误通知，并根据配置发送日志文件"""
        if not self.telegram_notifier:
            return

        try:
            # 发送错误通知
            self.telegram_notifier.send_error(error_message, error_title)

            # 如果启用了日志推送，则发送日志文件
            if self.config_manager.get("TELEGRAM_SEND_LOG_FILE", False):
                current_log_file = self.logger_manager.get_current_log_file()
                if current_log_file and os.path.exists(current_log_file):
                    try:
                        self.telegram_notifier.send_log_file(current_log_file)
                        self.logger.debug("错误日志文件已发送到Telegram")
                    except Exception as log_error:
                        self.logger.warning(f"发送错误日志文件失败: {log_error}")
        except Exception as notify_error:
            self.logger.warning(f"发送错误通知时出错: {notify_error}")

    def _send_execution_summary(self, overall_success: bool) -> None:
        """发送执行摘要"""
        if not self.telegram_notifier or not self.execution_start_time:
            return

        try:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 计算执行时长
            start_dt = datetime.strptime(self.execution_start_time, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            duration = end_dt - start_dt

            # 格式化时长
            total_seconds = int(duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            duration_str = f"{minutes}分{seconds}秒" if minutes > 0 else f"{seconds}秒"

            # 创建执行摘要
            summary = ExecutionSummary(
                username=self.config_manager.get("username", "未知用户"),
                start_time=self.execution_start_time,
                end_time=end_time,
                total_duration=duration_str,
                tasks=self.task_results,
                overall_success=overall_success,
            )

            # 发送摘要
            self.telegram_notifier.send_summary(summary)
            self.logger.debug("执行摘要已发送到Telegram")

            # 如果配置了发送日志文件，则发送当前日志文件
            if self.config_manager.get("TELEGRAM_SEND_LOG_FILE", False):
                current_log_file = self.logger_manager.get_current_log_file()
                if current_log_file and os.path.exists(current_log_file):
                    try:
                        self.telegram_notifier.send_log_file(current_log_file)
                        self.logger.debug("日志文件已发送到Telegram")
                    except Exception as log_error:
                        self.logger.warning(f"发送日志文件失败: {log_error}")

        except Exception as e:
            self.logger.warning(f"发送Telegram执行摘要失败: {e}")

    def _initialize_managers(self) -> bool:
        """
        初始化业务管理器

        Returns:
            是否初始化成功
        """
        try:
            driver = self.browser_manager.get_driver()
            if not driver:
                self.logger.error("浏览器驱动未初始化")
                return False

            # 初始化签到管理器
            auth_config = self.config_manager.get_auth_config()
            auth_config.update(self.config_manager.get_browser_config())
            self.signin_manager = SignInManager(driver, auth_config, self.logger)

            # 初始化拟人化行为管理器
            humanlike_config = self.config_manager.get_humanlike_config()
            humanlike_config.update(self.config_manager.get_browser_config())
            self.humanlike_manager = HumanlikeBehavior(
                driver, humanlike_config, self.logger
            )

            return True

        except Exception as e:
            self.logger.error(f"初始化业务管理器失败: {e}")
            return False

    def _create_browser(self) -> bool:
        """
        创建浏览器驱动

        Returns:
            是否创建成功
        """
        browser_config = self.config_manager.get_browser_config()
        return self.browser_manager.create_driver(browser_config)

    def _login_with_retry(self) -> bool:
        """
        带重试的登录

        Returns:
            是否登录成功
        """
        operation = "login"

        while self.retry_manager.can_retry(operation):
            try:
                if self.signin_manager.login():
                    self.retry_manager.reset(operation)
                    return True
                else:
                    retry_count = self.retry_manager.get_retry_count(operation)
                    remaining = self.retry_manager.get_remaining_retries(operation)
                    self.logger.warning(
                        f"登录失败，第 {retry_count} 次尝试，还剩 {remaining} 次重试机会"
                    )

            except Exception as e:
                retry_count = self.retry_manager.get_retry_count(operation)
                remaining = self.retry_manager.get_remaining_retries(operation)
                self.logger.error(
                    f"登录过程出错: {e}，第 {retry_count} 次尝试，还剩 {remaining} 次重试机会"
                )

        error_msg = "登录重试次数已达上限"
        self.logger.error(error_msg)

        # 发送错误通知
        self._send_error_with_log(error_msg, "登录失败")

        return False

    def _perform_humanlike_activities(self) -> None:
        """执行拟人化活动"""
        if not self.config_manager.get("enable_humanlike", False):
            self.logger.info("拟人化活动已禁用")
            self._record_task_result("browse", True, "拟人化活动已禁用，跳过执行")
            return

        try:
            self.logger.info("开始执行拟人化活动")
            self.humanlike_manager.perform_humanlike_activities()
            self.logger.info("拟人化活动执行完成")
            self._record_task_result("browse", True, "拟人化活动执行成功")

        except Exception as e:
            self.logger.warning(f"拟人化活动执行失败: {e}")
            self._record_task_result("browse", False, "拟人化活动执行失败", str(e))

    def _perform_signin(self) -> bool:
        """
        执行签到

        Returns:
            是否签到成功
        """
        if not self.config_manager.get("enable_checkin", True):
            self.logger.info("签到功能已禁用")
            self._record_task_result("signin", True, "签到功能已禁用，跳过执行")
            return True

        try:
            self.logger.info("开始执行签到")

            if self.signin_manager.sign_in():
                self.logger.info("签到完成")
                self._record_task_result("signin", True, "签到执行成功")
                return True
            else:
                error_msg = "签到失败"
                self.logger.error(error_msg)
                self._record_task_result("signin", False, "签到执行失败")

                # 发送签到失败通知
                self._send_error_with_log(error_msg, "签到操作失败")

                return False

        except Exception as e:
            error_msg = f"签到过程出错: {e}"
            self.logger.error(error_msg)
            self._record_task_result("signin", False, "签到过程出错", str(e))

            # 发送签到异常通知
            self._send_error_with_log(error_msg, "签到过程异常")

            return False

    def run(self) -> bool:
        """
        运行主流程

        Returns:
            是否执行成功
        """
        # 获取安全配置
        security_config = self.config_manager.get_security_config()
        timeout_seconds = security_config["timeout_seconds"]
        timeout_minutes = security_config["timeout_minutes"]

        self.logger.info(f"启动超时保护，超时时间: {timeout_minutes} 分钟")

        # 使用超时保护上下文管理器
        with TimeoutProtectionContext(self, timeout_seconds) as timeout_manager:
            # 记录开始时间
            self.execution_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                self.logger.info("开始98tang-autosign程序")

                if self.debug_mode:
                    self._log_debug_info()

                # 步骤1: 创建浏览器
                self.logger.debug("步骤1: 创建浏览器驱动")
                if not self._create_browser():
                    error_msg = "浏览器驱动创建失败"
                    self.logger.error(error_msg)

                    # 发送错误通知
                    self._send_error_with_log(error_msg, "浏览器初始化失败")

                    return False
                self.logger.debug("浏览器驱动创建成功")

                # 步骤2: 初始化业务管理器
                self.logger.debug("步骤2: 初始化业务管理器")
                if not self._initialize_managers():
                    error_msg = "业务管理器初始化失败"
                    self.logger.error(error_msg)

                    # 发送错误通知
                    self._send_error_with_log(error_msg, "系统初始化失败")

                    return False
                self.logger.debug("业务管理器初始化成功")

                # 步骤3: 登录
                self.logger.debug("步骤3: 执行登录流程")
                if not self._login_with_retry():
                    error_msg = "登录失败"
                    self.logger.error(error_msg)

                    # 发送登录失败摘要
                    self._send_execution_summary(False)

                    # 发送登录失败的错误通知（如果之前没有发送过）
                    self._send_error_with_log(error_msg, "程序执行失败")

                    return False
                self.logger.debug("登录流程完成")

                # 步骤4: 执行拟人化活动
                self.logger.debug("步骤4: 执行拟人化活动")
                self._perform_humanlike_activities()

                # 步骤5: 签到
                self.logger.debug("步骤5: 执行签到流程")
                if not self._perform_signin():
                    error_msg = "签到失败"
                    self.logger.error(error_msg)

                    # 发送签到失败摘要
                    self._send_execution_summary(False)

                    # 发送签到失败的错误通知
                    self._send_error_with_log(error_msg, "签到执行失败")

                    return False

                self.logger.info("程序执行完成")
                # 发送成功摘要
                self._send_execution_summary(True)
                return True

            except Exception as e:
                self.logger.error(f"程序运行失败: {e}")
                if self.debug_mode:
                    import traceback

                    self.logger.debug(f"详细错误信息: {traceback.format_exc()}")

                # 发送失败摘要
                self._send_execution_summary(False)

                # 发送错误通知
                self._send_error_with_log(str(e), "程序执行异常")

                return False

            finally:
                self._cleanup()

    def _log_debug_info(self) -> None:
        """输出调试信息"""
        self.logger.debug("运行配置信息:")
        self.logger.debug(f"  - 基础URL: {self.config_manager.get('base_url')}")
        self.logger.debug(f"  - 用户名: {self.config_manager.get('username')}")
        self.logger.debug(f"  - 无头模式: {self.config_manager.get('headless')}")
        self.logger.debug(
            f"  - 签到功能: {'启用' if self.config_manager.get('enable_checkin') else '禁用'}"
        )
        self.logger.debug(
            f"  - 拟人化活动: {'启用' if self.config_manager.get('enable_humanlike') else '禁用'}"
        )
        self.logger.debug(f"  - 最大重试次数: {self.retry_manager.max_retries}")

    def _cleanup(self) -> None:
        """清理资源"""
        self.logger.debug("开始清理资源")

        if self.browser_manager:
            self.browser_manager.quit_driver()

        self.logger.debug("资源清理完成")
