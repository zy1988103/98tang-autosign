# 98tang 自动签到工具

🎯 **98tang论坛自动签到工具** - 支持本地运行和Github Actions云端自动执行的智能签到系统

## ✨ 主要特性

- 🤖 **全自动签到**: 模拟真实用户行为，自动完成每日签到
- 🛡️ **安全提问处理**: 智能识别并回答安全提问，提高成功率
- 👤 **拟人化操作**: 随机延时、随机浏览、智能回复，避免被检测
- 📱 **Telegram通知**: 实时推送签到结果和日志文件
- ☁️ **Github Actions**: 支持云端自动运行，无需本地设备
- 🔧 **灵活配置**: 丰富的配置选项，满足不同使用需求
- 📝 **详细日志**: 完整的操作记录，便于调试和监控
- ⚡ **智能重试**: 失败自动重试机制，提高成功率

## 🏗️ 项目结构

```
98tang-autosign/
├── .github/workflows/
│   └── autosign.yml           # Github Actions工作流
├── src/                       # 源代码目录
│   ├── core/                  # 核心功能模块
│   ├── browser/               # 浏览器相关模块
│   ├── automation/            # 自动化操作模块
│   ├── notifications/         # 通知模块
│   └── utils/                 # 工具模块
├── main.py                    # 主入口文件
├── config.env.example         # 配置文件模板
├── requirements.txt           # 依赖包列表
├── LICENSE                    # MIT许可证
└── README.md                  # 项目说明
```

## 🚀 快速开始

### 方式一：Github Actions (推荐)

#### 1. Fork仓库
点击页面右上角的"Fork"按钮，将仓库复制到你的账号下。

#### 2. 配置Secrets
在你的仓库中，进入 `Settings` → `Secrets and variables` → `Actions`，添加以下必需配置：

**必需配置 (Secrets):**
```
SITE_USERNAME     # 你的98tang用户名
SITE_PASSWORD     # 你的98tang密码
```

**可选配置 (Secrets):**
```
# 安全提问配置
SECURITY_QUESTION    # 安全提问内容
SECURITY_ANSWER      # 安全提问答案

# Telegram通知配置
TELEGRAM_BOT_TOKEN   # Telegram机器人Token
TELEGRAM_CHAT_ID     # Telegram聊天ID
TELEGRAM_PROXY_URL   # Telegram代理URL（可选）
```

#### 3. 配置Variables
在 `Settings` → `Secrets and variables` → `Actions` → `Variables` 标签页，添加以下可选配置：

**基础配置:**
```
ENABLE_SECURITY_QUESTION=true    # 启用安全提问处理
ENABLE_CHECKIN=true              # 启用签到功能
BASE_URL=https://www.sehuatang.org  # 目标网站URL
```

**拟人化行为配置:**
```
ENABLE_REPLY=true                # 启用随机回复
REPLY_COUNT=2                    # 回复数量
ENABLE_RANDOM_BROWSING=true      # 启用随机浏览
BROWSE_PAGE_COUNT=3              # 浏览页面数量
REPLY_MESSAGES=感谢分享资源，收藏了;好资源收藏了，谢谢楼主;感谢楼主的精彩分享
```

**通知配置:**
```
ENABLE_TELEGRAM_NOTIFICATION=true  # 启用Telegram通知
TELEGRAM_SEND_LOG_FILE=false      # 发送日志文件
```

#### 4. 启用工作流
1. 进入 `Actions` 标签页
2. 点击 `98tang Auto Sign-in` 工作流
3. 点击 `Enable workflow`
4. 可以点击 `Run workflow` 进行测试

工作流将在每天北京时间上午9点自动运行。

### 方式二：本地运行

#### 1. 环境准备
确保系统已安装：
- Python 3.7 或更高版本
- Google Chrome 浏览器

#### 2. 下载代码
```bash
git clone https://github.com/your-username/98tang-autosign.git
cd 98tang-autosign
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置账号信息
```bash
# 复制配置模板
cp config.env.example config.env

# 编辑配置文件（使用你喜欢的编辑器）
nano config.env
```

在 `config.env` 中填写你的账号信息：
```env
# 必需配置
SITE_USERNAME=your_username
SITE_PASSWORD=your_password

# 可选：启用安全提问处理
ENABLE_SECURITY_QUESTION=true
SECURITY_QUESTION=你的安全提问
SECURITY_ANSWER=你的安全提问答案

# 可选：Telegram通知
ENABLE_TELEGRAM_NOTIFICATION=true
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

#### 5. 运行程序
```bash
python main.py
```

## ⚙️ 配置说明

### 本地运行配置参数 (config.env)

| 配置项 | 默认值 | 说明 | 必需 |
|--------|--------|------|------|
| **基本配置** | | | |
| `SITE_USERNAME` | - | 98tang用户名 | ✅ |
| `SITE_PASSWORD` | - | 98tang密码 | ✅ |
| `BASE_URL` | `https://www.sehuatang.org` | 目标网站URL | ❌ |
| **核心功能** | | | |
| `ENABLE_CHECKIN` | `true` | 启用签到功能 | ❌ |
| `ENABLE_SECURITY_QUESTION` | `false` | 启用安全提问处理 | ❌ |
| `SECURITY_QUESTION` | - | 安全提问内容 | ❌ |
| `SECURITY_ANSWER` | - | 安全提问答案 | ❌ |
| **拟人化行为** | | | |
| `ENABLE_REPLY` | `true` | 启用随机回复 | ❌ |
| `REPLY_COUNT` | `2` | 回复数量 (1-5) | ❌ |
| `ENABLE_RANDOM_BROWSING` | `true` | 启用随机浏览 | ❌ |
| `BROWSE_PAGE_COUNT` | `3` | 浏览页面数量 (1-10) | ❌ |
| `COMMENT_INTERVAL` | `15` | 回复间隔时间(秒) | ❌ |
| `WAIT_AFTER_LOGIN` | `5` | 登录后等待时间(秒) | ❌ |
| `REPLY_MESSAGES` | 预设回复内容 | 回复消息模板(用`;`分隔) | ❌ |
| **通知配置** | | | |
| `ENABLE_TELEGRAM_NOTIFICATION` | `false` | 启用Telegram通知 | ❌ |
| `TELEGRAM_BOT_TOKEN` | - | Telegram机器人Token | ❌ |
| `TELEGRAM_CHAT_ID` | - | Telegram聊天ID | ❌ |
| `TELEGRAM_PROXY_URL` | - | Telegram代理URL | ❌ |
| `TELEGRAM_SEND_LOG_FILE` | `true` | 发送日志文件 | ❌ |
| **系统配置** | | | |
| `HEADLESS` | `true` | 无头模式运行 | ❌ |
| `LOG_LEVEL` | `debug` | 日志级别 (DEBUG/INFO/WARNING/ERROR) | ❌ |
| `LOG_DIR` | `logs` | 日志保存目录 | ❌ |
| `MAX_LOG_FILES` | `7` | 最大日志文件数 | ❌ |
| **高级配置** | | | |
| `TIMING_MULTIPLIER` | `1.0` | 延时倍数 (0.5-3.0) | ❌ |
| `ENABLE_SMART_TIMING` | `true` | 启用智能延时 | ❌ |
| `MAX_RETRIES` | `3` | 最大重试次数 | ❌ |
| `TIMEOUT_MINUTES` | `5` | 超时时间(分钟) | ❌ |

### Github Actions 配置参数

#### Secrets (敏感信息)
| 配置项 | 说明 | 必需 |
|--------|------|------|
| `SITE_USERNAME` | 98tang用户名 | ✅ |
| `SITE_PASSWORD` | 98tang密码 | ✅ |
| `SECURITY_QUESTION` | 安全提问内容 | ❌ |
| `SECURITY_ANSWER` | 安全提问答案 | ❌ |
| `TELEGRAM_BOT_TOKEN` | Telegram机器人Token | ❌ |
| `TELEGRAM_CHAT_ID` | Telegram聊天ID | ❌ |
| `TELEGRAM_PROXY_URL` | Telegram代理URL | ❌ |

#### Variables (公开配置)
| 配置项 | 默认值 | 说明 | 必需 |
|--------|--------|------|------|
| **基本功能** | | | |
| `BASE_URL` | `https://www.sehuatang.org` | 目标网站URL | ❌ |
| `ENABLE_CHECKIN` | `true` | 启用签到功能 | ❌ |
| `ENABLE_SECURITY_QUESTION` | `false` | 启用安全提问处理 | ❌ |
| **拟人化行为** | | | |
| `ENABLE_REPLY` | `false` | 启用随机回复 | ❌ |
| `REPLY_COUNT` | `2` | 回复数量 | ❌ |
| `ENABLE_RANDOM_BROWSING` | `false` | 启用随机浏览 | ❌ |
| `BROWSE_PAGE_COUNT` | `3` | 浏览页面数量 | ❌ |
| `COMMENT_INTERVAL` | `15` | 回复间隔时间(秒) | ❌ |
| `WAIT_AFTER_LOGIN` | `5` | 登录后等待时间(秒) | ❌ |
| `REPLY_MESSAGES` | 预设回复内容 | 回复消息模板(用`;`分隔) | ❌ |
| **通知配置** | | | |
| `ENABLE_TELEGRAM_NOTIFICATION` | `false` | 启用Telegram通知 | ❌ |
| `TELEGRAM_SEND_LOG_FILE` | `false` | 发送日志文件 | ❌ |
| **系统配置** | | | |
| `LOG_LEVEL` | `INFO` | 日志级别 | ❌ |
| `MAX_LOG_FILES` | `7` | 最大日志文件数 | ❌ |
| `TIMING_MULTIPLIER` | `1.0` | 延时倍数 | ❌ |
| `ENABLE_SMART_TIMING` | `true` | 启用智能延时 | ❌ |
| `MAX_RETRIES` | `3` | 最大重试次数 | ❌ |
| `TIMEOUT_MINUTES` | `5` | 超时时间(分钟) | ❌ |

> **注意**: 
> - ✅ 表示必需配置，❌ 表示可选配置
> - Github Actions中 `HEADLESS` 强制为 `true`
> - Secrets用于存储敏感信息，Variables用于存储公开配置

## ❓ 常见问题

### Q: Github Actions运行失败怎么办？
A: 检查以下几点：
1. 确保已正确配置 `SITE_USERNAME` 和 `SITE_PASSWORD`
2. 检查账号密码是否正确
3. 查看Actions日志了解具体错误信息
4. 确保仓库已启用Actions功能

### Q: 本地运行时Chrome驱动问题？
A: 程序会自动管理Chrome驱动，如遇问题：
```bash
pip install --upgrade selenium webdriver-manager
```

### Q: 如何修改签到时间？
A: 编辑 `.github/workflows/autosign.yml` 文件中的 `cron` 表达式：
```yaml
schedule:
  - cron: '0 1 * * *'  # UTC时间1点 = 北京时间9点
```

### Q: 安全提问如何配置？
A: 登录网站查看你的安全提问，然后在配置中填写：
```env
SECURITY_QUESTION=你设置的安全提问
SECURITY_ANSWER=对应的答案
```

### Q: Telegram通知收不到？
A: 检查以下配置：
1. 机器人Token是否正确
2. Chat ID是否正确
3. 机器人是否已添加到对应群组
4. 网络是否能访问Telegram API

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 提交Issue
- 使用清晰的标题描述问题
- 提供详细的复现步骤
- 附上相关的日志信息

### 提交代码
1. Fork本仓库
2. 创建特性分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -m 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建Pull Request

## 📄 许可证

本项目采用 [MIT许可证](LICENSE)。

## ⚠️ 免责声明

本工具仅供学习和研究使用。使用者应遵守目标网站的使用条款和相关法律法规。作者不承担任何因使用本工具而产生的责任。

## 🌟 支持项目

如果这个项目对你有帮助，欢迎给个Star ⭐️

---

**Happy Coding! 🚀**