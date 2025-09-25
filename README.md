# 98tang 自动签到工具

🎯 **98tang论坛自动签到工具** - 支持本地运行和Github Actions云端自动执行的智能签到系统

## ✨ 主要特性

- 🤖 **全自动签到**: 模拟真实用户行为，自动完成每日签到
- 🛡️ **安全提问处理**: 智能识别并回答安全提问，提高成功率
- 👤 **拟人化操作**: 随机延时、随机浏览、智能回复，避免被检测
- 📱 **Telegram通知**: 实时推送签到结果和日志文件
- ☁️ **Github Actions**: 支持云端自动运行，无需本地设备
- ⚡ **智能重试**: 失败自动重试机制，提高成功率

## 🏗️ 项目结构

```
98tang-autosign/
├── .github/workflows/     # Github Actions工作流
├── src/                   # 源代码目录
├── docs/                  # 项目文档
├── main.py               # 主入口文件
├── config.env.example    # 配置文件模板
└── requirements.txt      # 依赖包列表
```

## 🚀 快速开始

### Github Actions (推荐)
1. Fork仓库到你的账号下
2. 在仓库设置中配置 Secrets 和 Variables
3. 启用工作流，每天自动运行

### 本地运行
1. 克隆仓库并安装依赖
2. 复制并编辑配置文件
3. 运行 `python main.py`

> 📖 **详细安装指南**: [installation.md](docs/installation.md)

## ⚙️ 配置参数

| 参数名 | 默认值 | 说明 | 必需 | 类别 |
|--------|--------|------|------|------|
| **基本配置** | | | | |
| `SITE_USERNAME` | - | 98tang用户名 | ✅ | 基本 |
| `SITE_PASSWORD` | - | 98tang密码 | ✅ | 基本 |
| `BASE_URL` | `https://www.sehuatang.org` | 目标网站URL | ❌ | 基本 |
| **功能开关** | | | | |
| `ENABLE_CHECKIN` | `true` | 启用签到功能 | ❌ | 功能 |
| `ENABLE_SECURITY_QUESTION` | `false` | 启用安全提问处理 | ❌ | 功能 |
| `SECURITY_QUESTION` | - | 安全提问内容 | ❌ | 功能 |
| `SECURITY_ANSWER` | - | 安全提问答案 | ❌ | 功能 |
| **拟人化行为** | | | | |
| `ENABLE_REPLY` | `true` | 启用随机回复 | ❌ | 行为 |
| `REPLY_COUNT` | `2` | 回复数量 (1-5) | ❌ | 行为 |
| `ENABLE_RANDOM_BROWSING` | `true` | 启用随机浏览 | ❌ | 行为 |
| `BROWSE_PAGE_COUNT` | `3` | 浏览页面数量 (1-10) | ❌ | 行为 |
| `COMMENT_INTERVAL` | `15` | 回复间隔时间(秒) | ❌ | 行为 |
| `WAIT_AFTER_LOGIN` | `5` | 登录后等待时间(秒) | ❌ | 行为 |
| `REPLY_MESSAGES` | 预设回复内容 | 回复消息模板(用`;`分隔) | ❌ | 行为 |
| **通知配置** | | | | |
| `ENABLE_TELEGRAM_NOTIFICATION` | `false` | 启用Telegram通知 | ❌ | 通知 |
| `TELEGRAM_BOT_TOKEN` | - | Telegram机器人Token | ❌ | 通知 |
| `TELEGRAM_CHAT_ID` | - | Telegram聊天ID | ❌ | 通知 |
| `TELEGRAM_PROXY_URL` | - | Telegram代理URL | ❌ | 通知 |
| `TELEGRAM_SEND_LOG_FILE` | `true` | 发送日志文件 | ❌ | 通知 |
| **系统配置** | | | | |
| `HEADLESS` | `true` | 无头模式运行 | ❌ | 系统 |
| `LOG_LEVEL` | `debug` | 日志级别 (DEBUG/INFO/WARNING/ERROR) | ❌ | 系统 |
| `LOG_DIR` | `logs` | 日志保存目录 | ❌ | 系统 |
| `MAX_LOG_FILES` | `7` | 最大日志文件数 | ❌ | 系统 |
| **高级配置** | | | | |
| `TIMING_MULTIPLIER` | `1.0` | 延时倍数 (0.5-3.0) | ❌ | 高级 |
| `ENABLE_SMART_TIMING` | `true` | 启用智能延时 | ❌ | 高级 |
| `MAX_RETRIES` | `3` | 最大重试次数 | ❌ | 高级 |
| `TIMEOUT_MINUTES` | `5` | 超时时间(分钟) | ❌ | 高级 |

> **配置说明**：
> - ✅ 必需配置，❌ 可选配置
> - **本地运行**：在 `config.env` 文件中配置
> - **Github Actions**：敏感信息在 Secrets 中配置，其他在 Variables 中配置

## 📚 文档

- 📦 [安装指南](docs/installation.md) - 详细的安装和配置步骤
- ❓ [常见问题](docs/faq.md) - FAQ和解决方案
- 🤝 [贡献指南](docs/contributing.md) - 如何参与项目开发

## ❓ 快速问答

**Q: 如何开始使用？**  
A: 1. Fork仓库到你的账号 → 2. 配置Secrets（用户名密码） → 3. 启用Actions工作流 → 4. 程序将每天自动签到

**Q: 需要配置哪些信息？**  
A: 必需：`SITE_USERNAME`和`SITE_PASSWORD`；可选：安全提问、Telegram通知等

**Q: 多久运行一次？**  
A: 工作流每天北京时间上午9点自动运行，也可以手动触发测试

**Q: 配置错误怎么办？**  
A: 查看 [FAQ文档](docs/faq.md) 或提交Issue

**Q: 想要参与开发？**  
A: 参考 [贡献指南](docs/contributing.md) 了解开发流程

## 📄 许可证

本项目采用 [MIT许可证](LICENSE)。

## ⚠️ 免责声明

本工具仅供学习和研究使用。使用者应遵守目标网站的使用条款和相关法律法规。

---

⭐ 如果这个项目对你有帮助，欢迎给个Star！