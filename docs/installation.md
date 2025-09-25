# 安装指南

## 方式一：Github Actions (推荐)

### 1. Fork仓库
点击页面右上角的"Fork"按钮，将仓库复制到你的账号下。

### 2. 配置环境和密钥

Github Actions支持两种配置方式，推荐使用Environment Secrets：

#### 🔒 方式A：Environment Secrets (推荐)

**步骤1：创建环境**
1. 在你的仓库中，进入 `Settings` → `Environments`
2. 点击 `New environment`
3. 环境名称输入：`98tang-autosign`
4. 点击 `Configure environment`

**步骤2：配置Environment Secrets**
在 `98tang-autosign` 环境页面的 `Environment secrets` 部分：

**必需配置 (Environment Secrets):**
```
SITE_USERNAME     # 你的98tang用户名
SITE_PASSWORD     # 你的98tang密码
```

**可选配置 (Environment Secrets):**
```
# 安全提问配置
SECURITY_QUESTION    # 安全提问内容
SECURITY_ANSWER      # 安全提问答案

# Telegram通知配置
TELEGRAM_BOT_TOKEN   # Telegram机器人Token
TELEGRAM_CHAT_ID     # Telegram聊天ID
TELEGRAM_PROXY_URL   # Telegram代理URL（可选）
```

**步骤3：配置Environment Variables (可选)**
在同一页面的 `Environment variables` 部分，可以配置其他选项如：
```
# 拟人化行为配置
ENABLE_REPLY=true
REPLY_COUNT=2
ENABLE_RANDOM_BROWSING=true

# Telegram通知配置
ENABLE_TELEGRAM_NOTIFICATION=true
TELEGRAM_SEND_LOG_FILE=true        # 发送日志文件
TELEGRAM_SEND_SCREENSHOT=true      # 发送页面截图

# 等等其他配置项
```

#### 🔧 方式B：Repository Secrets (兼容模式)

如果不想创建环境，可以直接使用Repository Secrets：

1. 进入 `Settings` → `Secrets and variables` → `Actions`
2. 在 `Repository secrets` 部分添加必需配置
3. 在 `Variables` 标签页添加其他配置选项

> **💡 说明**: 系统会优先尝试使用`98tang-autosign`环境的Environment Secrets，如果环境不存在或配置不完整，会自动回退到Repository Secrets模式。

> **🔒 安全优势**: Environment Secrets提供更好的安全性和权限管理，可以限制特定环境的访问权限。

### 3. 启用工作流
1. 进入 `Actions` 标签页
2. 点击 `98tang Auto Sign-in` 工作流
3. 点击 `Enable workflow`
4. 可以点击 `Run workflow` 进行测试

### 4. 验证配置
运行工作流后，检查日志输出：
- ✅ 如果显示 "Environment secrets模式: 98tang-autosign"，说明使用了推荐的环境配置
- ⚠️ 如果显示 "Repository secrets模式 - 回退模式"，说明使用了兼容模式

工作流将在每天北京时间上午9点自动运行。

## 方式二：本地运行

### 1. 环境准备
确保系统已安装：
- Python 3.7 或更高版本
- Google Chrome 浏览器

### 2. 下载代码
```bash
git clone https://github.com/your-username/98tang-autosign.git
cd 98tang-autosign
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置账号信息
```bash
# 复制配置模板
cp config.env.example config.env

# 编辑配置文件（使用你喜欢的编辑器）
nano config.env
```

在 `config.env` 中填写你的账号信息，具体配置参数请参考 `config.env.example` 文件中的注释说明。

### 5. 运行程序
```bash
python main.py
```
