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
2. 创建 `98tang-autosign` 环境并配置 Environment Secrets (推荐)
3. 或者直接配置 Repository Secrets (兼容模式)
4. 启用工作流，每天自动运行

### 本地运行
1. 克隆仓库并安装依赖
2. 复制并编辑配置文件
3. 运行 `python main.py`

> 📖 **详细安装指南**: [installation.md](docs/installation.md)

## ⚙️ 配置参数

### 🔑 必备配置
| 参数名 | 说明 | 示例值 |
|--------|------|--------|
| `SITE_USERNAME` | 98tang论坛用户名 | `your_username` |
| `SITE_PASSWORD` | 98tang论坛密码 | `your_password` |

### 🔧 基础功能配置
| 参数名 | 默认值 | 说明 | 推荐设置 |
|--------|--------|------|----------|
| `BASE_URL` | `https://www.sehuatang.org` | 目标网站地址 | 保持默认 |
| `ENABLE_CHECKIN` | `true` | 是否执行签到 | `true` |
| `ENABLE_SECURITY_QUESTION` | `false` | 是否处理安全提问 | 有安全提问时设为`true` |
| `SECURITY_QUESTION` | - | 你的安全提问内容 | 如：`你的生日是？` |
| `SECURITY_ANSWER` | - | 安全提问的答案 | 如：`1990-01-01` |

### 📱 Telegram通知配置
| 参数名 | 默认值 | 说明 | 获取方法 |
|--------|--------|------|----------|
| `ENABLE_TELEGRAM_NOTIFICATION` | `false` | 是否启用通知 | 需要时设为`true` |
| `TELEGRAM_BOT_TOKEN` | - | 机器人Token | 找@BotFather申请 |
| `TELEGRAM_CHAT_ID` | - | 聊天ID | 找@userinfobot获取 |
| `TELEGRAM_PROXY_URL` | - | 代理地址(可选) | 网络受限时使用 |
| `TELEGRAM_SEND_LOG_FILE` | `true` | 是否发送日志文件 | `true` (便于调试) |

### 🤖 拟人化行为配置
<details>
<summary>点击展开查看拟人化设置</summary>

| 参数名 | 默认值 | 说明 | 建议值 |
|--------|--------|------|--------|
| `ENABLE_REPLY` | `true` | 是否随机回复帖子 | `true` (更像真人) |
| `REPLY_COUNT` | `2` | 每次回复帖子数量 | `1-3` (适中) |
| `ENABLE_RANDOM_BROWSING` | `true` | 是否随机浏览页面 | `true` (增加真实性) |
| `BROWSE_PAGE_COUNT` | `3` | 浏览页面数量 | `2-5` (不要太多) |
| `COMMENT_INTERVAL` | `15` | 回复间隔时间(秒) | `10-30` (避免频繁操作) |
| `WAIT_AFTER_LOGIN` | `5` | 登录后等待时间(秒) | `3-10` (模拟人工操作) |
| `REPLY_MESSAGES` | 预设内容 | 回复模板(`;`分隔) | 自定义友好回复 |

</details>

### ⚡ 高级配置
<details>
<summary>点击展开查看高级设置</summary>

| 参数名 | 默认值 | 说明 | 调整建议 |
|--------|--------|------|----------|
| `HEADLESS` | `true` | 无界面模式 | Actions必须为`true` |
| `LOG_LEVEL` | `debug` | 日志详细程度 | `info`(生产) / `debug`(调试) |
| `TIMING_MULTIPLIER` | `1.0` | 操作速度倍数 | `0.8-1.5` (慢一点更安全) |
| `MAX_RETRIES` | `3` | 失败重试次数 | `2-5` (适中即可) |
| `TIMEOUT_MINUTES` | `5` | 整体超时时间 | `3-10` (根据网络调整) |

</details>

> **📋 配置方式**：
> - **Github Actions (推荐)**: 创建`98tang-autosign`环境，在Environment Secrets中配置敏感信息
> - **Github Actions (兼容)**: 直接在Repository Secrets中配置，系统自动回退使用
> - **本地运行**: 所有配置都在`config.env`文件中
> 
> **💡 新手建议**: 只需配置必需参数即可正常使用，其他保持默认值
> 
> **🔒 安全说明**: Environment Secrets提供更好的安全性和权限管理，推荐使用

## 📚 文档

- 📦 [安装指南](docs/installation.md) - 详细的安装和配置步骤
- ❓ [常见问题](docs/faq.md) - FAQ和解决方案
- 🤝 [贡献指南](docs/contributing.md) - 如何参与项目开发

## ❓ 快速问答

**Q: 如何开始使用？**  
A: 1. Fork仓库到你的账号 → 2. 创建`98tang-autosign`环境并配置Environment Secrets（用户名密码） → 3. 启用Actions工作流 → 4. 程序将每天自动签到

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