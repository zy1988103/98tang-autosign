"""
Telegram Bot 通知模块

提供通过Telegram Bot发送通知的功能
"""

import json
import logging
import requests
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class TaskResult:
    """任务执行结果"""

    task_type: str  # 任务类型：signin, reply, browse
    success: bool  # 是否成功
    message: str  # 结果消息
    details: Optional[str] = None  # 详细信息
    timestamp: Optional[str] = None  # 执行时间

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class ExecutionSummary:
    """执行摘要"""

    username: str
    start_time: str
    end_time: str
    total_duration: str
    tasks: List[TaskResult]
    overall_success: bool

    def to_message(self) -> str:
        """转换为美观的Telegram消息格式"""
        status_emoji = "✅" if self.overall_success else "❌"
        status_text = "成功" if self.overall_success else "失败"

        # 统计任务结果
        success_count = sum(1 for task in self.tasks if task.success)
        total_count = len(self.tasks)

        message = f"""*98tang\\-autosign 执行报告*

*账号:* `{self.username}`
*日期:* `{self.start_time.split()[0]}`
*开始时间:* `{self.start_time.split()[1]}`
*结束时间:* `{self.end_time.split()[1]}`
*总耗时:* `{self.total_duration}`
*执行状态:* {status_emoji} *{status_text}*
*任务统计:* `{success_count}/{total_count}` 成功

*任务详情:*
"""

        for task in self.tasks:
            task_emoji = "✅" if task.success else "❌"
            task_name = {
                "signin": "签到",
                "reply": "回帖",
                "browse": "拟真浏览",
            }.get(task.task_type, task.task_type)

            message += f"{task_emoji} *{task_name}:* `{task.message}`\n"
            if task.details:
                # 转义特殊字符
                details_escaped = (
                    task.details.replace("_", "\\_")
                    .replace("*", "\\*")
                    .replace("[", "\\[")
                    .replace("]", "\\]")
                    .replace("(", "\\(")
                    .replace(")", "\\)")
                    .replace("~", "\\~")
                    .replace("`", "\\`")
                    .replace(">", "\\>")
                    .replace("#", "\\#")
                    .replace("+", "\\+")
                    .replace("-", "\\-")
                    .replace("=", "\\=")
                    .replace("|", "\\|")
                    .replace("{", "\\{")
                    .replace("}", "\\}")
                    .replace(".", "\\.")
                    .replace("!", "\\!")
                )
                message += f"  _{details_escaped}_\n"

        return message.strip()


class TelegramNotifier:
    """Telegram Bot 通知器"""

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        proxy_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        初始化Telegram通知器

        Args:
            bot_token: Telegram Bot Token
            chat_id: Telegram Chat ID
            proxy_url: 代理URL（可选）
            logger: 日志器
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.proxy_url = proxy_url or "https://api.telegram.org"
        self.logger = logger or logging.getLogger(__name__)

        # 确保代理URL格式正确
        if not self.proxy_url.startswith("http"):
            self.proxy_url = f"https://{self.proxy_url}"

        # 移除尾部斜杠
        self.proxy_url = self.proxy_url.rstrip("/")

        self.api_url = f"{self.proxy_url}/bot{self.bot_token}"

        # 验证配置
        self._validate_config()

    def _validate_config(self) -> None:
        """验证配置"""
        if not self.bot_token:
            raise ValueError("Telegram Bot Token 不能为空")
        if not self.chat_id:
            raise ValueError("Telegram Chat ID 不能为空")

        self.logger.debug(f"Telegram通知器初始化完成，使用API: {self.proxy_url}")

    def send_message(self, message: str, parse_mode: str = "MarkdownV2") -> bool:
        """
        发送消息到Telegram

        Args:
            message: 要发送的消息
            parse_mode: 解析模式 (Markdown/HTML)

        Returns:
            是否发送成功
        """
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode,
            }

            self.logger.debug(f"发送Telegram消息: {message[:100]}...")

            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    self.logger.debug("Telegram消息发送成功")
                    return True
                else:
                    self.logger.error(
                        f"Telegram API返回错误: {result.get('description', '未知错误')}"
                    )
                    return False
            else:
                self.logger.error(
                    f"Telegram消息发送失败，HTTP状态码: {response.status_code}"
                )
                self.logger.debug(f"响应内容: {response.text}")
                return False

        except requests.exceptions.Timeout:
            self.logger.error("Telegram消息发送超时")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Telegram消息发送失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Telegram消息发送异常: {e}")
            return False

    def send_summary(self, summary: ExecutionSummary) -> bool:
        """
        发送执行摘要

        Args:
            summary: 执行摘要

        Returns:
            是否发送成功
        """
        return self.send_message(summary.to_message())

    def send_log_file(self, log_file_path: str) -> bool:
        """
        发送日志文件

        Args:
            log_file_path: 日志文件路径

        Returns:
            是否发送成功
        """
        try:
            if not os.path.exists(log_file_path):
                self.logger.error(f"日志文件不存在: {log_file_path}")
                return False

            url = f"{self.api_url}/sendDocument"

            with open(log_file_path, "rb") as f:
                files = {"document": f}
                data = {
                    "chat_id": self.chat_id,
                    "caption": f'📄 *98tang\\-autosign 日志文件*\n\n📅 生成时间: `{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}`',
                    "parse_mode": "MarkdownV2",
                }

                self.logger.debug(f"发送日志文件: {log_file_path}")

                response = requests.post(url, files=files, data=data, timeout=60)

                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        self.logger.debug("日志文件发送成功")
                        return True
                    else:
                        self.logger.error(
                            f"Telegram API返回错误: {result.get('description', '未知错误')}"
                        )
                        return False
                else:
                    self.logger.error(
                        f"日志文件发送失败，HTTP状态码: {response.status_code}"
                    )
                    self.logger.debug(f"响应内容: {response.text}")
                    return False

        except requests.exceptions.Timeout:
            self.logger.error("日志文件发送超时")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"日志文件发送失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"日志文件发送异常: {e}")
            return False

    def test_connection(self) -> bool:
        """
        测试连接

        Returns:
            是否连接成功
        """
        test_message = f"""
🧪 *98tang\\-autosign 连接测试*

✅ Telegram Bot 连接正常
⏰ 测试时间: `{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}`

如果您看到这条消息，说明通知配置成功！
"""

        return self.send_message(test_message.strip())

    def send_document(self, document_path: str, caption: str = None) -> bool:
        """
        发送文档文件

        Args:
            document_path: 文档文件路径
            caption: 文档说明（可选）

        Returns:
            是否发送成功
        """
        try:
            if not os.path.exists(document_path):
                self.logger.error(f"文档文件不存在: {document_path}")
                return False

            url = f"{self.api_url}/sendDocument"

            with open(document_path, "rb") as f:
                files = {"document": f}
                data = {
                    "chat_id": self.chat_id,
                }

                # 如果提供了说明，添加到请求中
                if caption:
                    # 转义MarkdownV2格式的特殊字符
                    def escape_markdown_v2(text):
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

                    data["caption"] = escape_markdown_v2(caption)
                    data["parse_mode"] = "MarkdownV2"

                self.logger.debug(f"发送文档: {document_path}")

                response = requests.post(url, files=files, data=data, timeout=60)

                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        self.logger.debug("文档发送成功")
                        return True
                    else:
                        self.logger.error(
                            f"Telegram API返回错误: {result.get('description', '未知错误')}"
                        )
                        return False
                else:
                    self.logger.error(
                        f"文档发送失败，HTTP状态码: {response.status_code}"
                    )
                    self.logger.debug(f"响应内容: {response.text}")
                    return False

        except requests.exceptions.Timeout:
            self.logger.error("文档发送超时")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"文档发送失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"文档发送异常: {e}")
            return False

    def send_error(self, error_message: str, error_type: str = "程序错误") -> bool:
        """
        发送错误通知

        Args:
            error_message: 错误消息
            error_type: 错误类型

        Returns:
            是否发送成功
        """
        # 转义特殊字符
        escaped_error = (
            error_message.replace("_", "\\_")
            .replace("*", "\\*")
            .replace("[", "\\[")
            .replace("]", "\\]")
            .replace("(", "\\(")
            .replace(")", "\\)")
            .replace("~", "\\~")
            .replace("`", "\\`")
            .replace(">", "\\>")
            .replace("#", "\\#")
            .replace("+", "\\+")
            .replace("-", "\\-")
            .replace("=", "\\=")
            .replace("|", "\\|")
            .replace("{", "\\{")
            .replace("}", "\\}")
            .replace(".", "\\.")
            .replace("!", "\\!")
        )
        escaped_type = (
            error_type.replace("_", "\\_")
            .replace("*", "\\*")
            .replace("[", "\\[")
            .replace("]", "\\]")
            .replace("(", "\\(")
            .replace(")", "\\)")
            .replace("~", "\\~")
            .replace("`", "\\`")
            .replace(">", "\\>")
            .replace("#", "\\#")
            .replace("+", "\\+")
            .replace("-", "\\-")
            .replace("=", "\\=")
            .replace("|", "\\|")
            .replace("{", "\\{")
            .replace("}", "\\}")
            .replace(".", "\\.")
            .replace("!", "\\!")
        )

        message = f"""
🚨 *98tang\\-autosign 错误报告*

❌ *错误类型*: `{escaped_type}`
⏰ *时间*: `{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}`

📋 *错误详情*:
```
{escaped_error}
```
"""

        return self.send_message(message.strip())
