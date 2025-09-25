# 安装指南

## 方式一：Github Actions (推荐)

### 1. Fork仓库
点击页面右上角的"Fork"按钮，将仓库复制到你的账号下。

### 2. 配置Secrets
在你的仓库中，进入 `Settings` → `Secrets and variables` → `Actions`，添加以下配置：

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

### 3. 配置Variables
在 `Settings` → `Secrets and variables` → `Actions` → `Variables` 标签页，添加其他配置选项。

### 4. 启用工作流
1. 进入 `Actions` 标签页
2. 点击 `98tang Auto Sign-in` 工作流
3. 点击 `Enable workflow`
4. 可以点击 `Run workflow` 进行测试

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
