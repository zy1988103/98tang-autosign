<div align="center">

# 🎯 98tang AutoSign

**智能化98堂论坛自动签到系统 | 支持云端部署 | 拟人化操作**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/) [![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-supported-green.svg)](https://github.com/features/actions) [![Selenium](https://img.shields.io/badge/Selenium-4.15+-orange.svg)](https://selenium-python.readthedocs.io/) 
[![GitHub stars](https://img.shields.io/github/stars/WizisCool/98tang-autosign?style=social)](https://github.com/WizisCool/98tang-autosign/stargazers) [![GitHub forks](https://img.shields.io/github/forks/WizisCool/98tang-autosign?style=social)](https://github.com/WizisCool/98tang-autosign/network/members)

[📖 文档](#-文档) • [🚀 快速开始](#-快速开始) • [⚙️ 配置](#️-配置参数) • [🤝 贡献](#-贡献)

</div>

---

## ✨ 核心特性

<div align="center">

| 🤖 **拟人化系统** | 🛡️ **反检测技术** |
|:------------------|:------------------|
| • **智能登录**: 无Cookies依赖的深度登录模拟<br>• **拟人化浏览**: 页面Payload智能分配行为<br>• **智能回帖**: 待完善<br>• **多选择器**: 使用多种选择器确保长期可用 | • **反脚本检测**: 使用undetected-chromedriver<br>• **行为分析**: 根据页面复杂程度判断行为<br>• **拟人操作**: 根据行为模拟滚动等真人操作<br>• **逻辑模拟**: 不直接访问URL采用模拟点击 |

| ☁️ **云端部署** | 📱 **消息通知** |
|:----------------|:----------------|
| • **GitHub Actions**: 免费的云端自动运行<br>• **一键部署**: 不需要复杂本地环境搭建<br>• **随机调度**: 每日0:00~0:30随机时间执行<br>• **日志保存**: 30天的运行日志，方便排查问题 | • **Telegram推送**: 定时签到结果通知<br>• **截图功能**: 真实的浏览器截图推送<br>• **日志推送**: 详细的DEBUG日志推送<br>• **错误提醒**: 统一集中的错误管理 |

</div>

---

## 🏗️ 项目架构

```
98tang-autosign/
├── 📁 .github/workflows/    # GitHub Actions 工作流
│   └── autosign.yml         # 自动签到工作流配置
├── 📁 src/                  # 核心源代码
│   ├── 📁 automation/       # 自动化逻辑模块
│   ├── 📁 browser/          # 浏览器操作封装
│   ├── 📁 core/             # 核心功能模块
│   ├── 📁 notifications/    # 通知系统
│   └── 📁 utils/            # 工具函数库
├── 📁 docs/                 # 项目文档
│   ├── installation.md     # 详细安装指南
│   ├── configuration.md    # 完整配置文档
│   ├── faq.md              # 常见问题解答
│   └── contributing.md     # 贡献者指南
├── 📄 main.py              # 程序入口文件
├── 📄 config.env.example   # 配置文件模板
├── 📄 requirements.txt     # Python依赖列表
└── 📄 README.md           # 项目说明文档
```

---

## 🚀 快速开始

### 🎯 方式一：GitHub Actions（推荐）

> ✅ **零成本 | 免维护 | 自动运行**

<details>
<summary>🔧 <b>点击展开详细配置步骤</b></summary>

#### 1️⃣ Fork 仓库
点击页面右上角 **Fork** 按钮，将项目复制到您的账号下

#### 2️⃣ 配置环境变量（推荐方式）
1. 进入您的仓库 → `Settings` → `Environments`
2. 创建新环境，名称：`98tang-autosign`
3. 在 Environment secrets 中添加：
   ```
   SITE_USERNAME     # 您的98tang用户名
   SITE_PASSWORD     # 您的98tang密码
   ```

#### 3️⃣ 启用工作流
1. 进入 `Actions` 标签页
2. 点击 `98tang Auto Sign-in` 工作流
3. 点击 `Enable workflow` 启用
4. 可选：点击 `Run workflow` 立即测试

#### 4️⃣ 验证配置
查看 Actions 运行日志：
- ✅ `Environment secrets模式: 98tang-autosign` - 配置成功
- ⚠️ `Repository secrets模式 - 回退模式` - 使用备用配置

</details>

### 🖥️ 方式二：本地运行

<details>
<summary>💻 <b>点击展开本地部署步骤</b></summary>

#### 环境要求
- Python 3.7+ 
- Google Chrome 浏览器

#### 安装步骤
```bash
# 1. 克隆仓库
git clone https://github.com/your-username/98tang-autosign.git
cd 98tang-autosign

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置账号信息
cp config.env.example config.env
# 编辑 config.env 文件，填入您的账号信息

# 4. 运行程序
python main.py
```

</details>

---

## ⚙️ 配置参数

### 🔑 必备配置

| 参数名 | 说明 | 示例值 |
|--------|------|--------|
| `SITE_USERNAME` | 98tang论坛用户名 | `your_username` |
| `SITE_PASSWORD` | 98tang论坛密码 | `your_password` |

### 📋 完整配置说明

本项目支持高度自定义配置参数，涵盖以下功能模块：

- 🔐 **基础配置**: 账号信息、网站设置
- 🛡️ **安全提问**: 安全验证配置  
- 📱 **Telegram通知**: 消息推送、文件发送
- 🤖 **拟人化行为**: 随机回复、浏览行为
- ⚡ **高级设置**: 性能调优、调试选项

> 📖 **详细配置文档**: [configuration.md](docs/configuration.md)  
> 包含所有参数的详细说明、默认值、示例和使用注意事项



### 💡 配置方式对比

| 配置方式 | 安全性 | 易用性 | 推荐度 | 适用场景 |
|----------|--------|--------|--------|----------|
| **Environment Secrets** | 🔒🔒🔒 | ⭐⭐⭐ | ✅ **推荐** | 因为是我用的 |
| **Repository Secrets** | 🔒🔒 | ⭐⭐⭐⭐ | ✅ 备用 | 个人项目，快速配置 |
| **本地配置文件** | 🔒 | ⭐⭐⭐⭐⭐ | 💻 开发 | 本地开发部署 |

---

## 📚 文档

| 文档 | 描述 | 链接 |
|------|------|------|
| 📦 **安装指南** | 详细的安装和配置步骤 | [installation.md](docs/installation.md) |
| ⚙️ **配置文档** | 完整的配置参数说明 | [configuration.md](docs/configuration.md) |
| ❓ **常见问题** | FAQ和故障排除 | [faq.md](docs/faq.md) |
| 🤝 **贡献指南** | 参与项目开发指南 | [contributing.md](docs/contributing.md) |

---

## 📊 使用统计

<div align="center">

![GitHub repo size](https://img.shields.io/github/repo-size/WizisCool/98tang-autosign) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/WizisCool/98tang-autosign) ![GitHub last commit](https://img.shields.io/github/last-commit/WizisCool/98tang-autosign)

</div>

---

## 🔄 更新日志

### 🆕 最新版本 v2.1.0
- ✨ 新增智能签到状态检测
- 🛡️ 修复统计信息误判问题  
- 📱 优化Telegram通知机制
- 🎨 全新专业化README设计
- 🔧 增强GitHub Actions稳定性

<details>
<summary>查看完整更新历史</summary>

### v2.0.0
- 🚀 重构核心架构，模块化设计
- ☁️ 完善GitHub Actions支持
- 📱 集成Telegram通知系统
- 🤖 增强拟人化行为模拟

### v1.5.0  
- 🛡️ 新增安全提问处理
- 🎯 优化签到成功率
- 📝 完善文档和配置说明

</details>

---

## 🤝 贡献

我们欢迎所有形式的贡献！

### 💝 贡献方式

- 🐛 **报告Bug**: [提交Issue](https://github.com/WizisCool/98tang-autosign/issues/new?template=bug_report.md)
- 💡 **功能建议**: [功能请求](https://github.com/WizisCool/98tang-autosign/issues/new?template=feature_request.md)  
- 🔧 **代码贡献**: [提交PR](https://github.com/WizisCool/98tang-autosign/pulls)
- 📖 **文档改进**: 帮助完善文档

### 👥 贡献者

感谢所有为项目做出贡献的开发者！

<a href="https://github.com/WizisCool/98tang-autosign/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=WizisCool/98tang-autosign" />
</a>

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) - 查看 LICENSE 文件了解详情

---

## ⚠️ 免责声明

本工具仅供学习和研究使用。使用者应遵守目标网站的使用条款和相关法律法规。开发者不对使用本工具产生的任何后果承担责任。

---

<div align="center">

**如果这个项目对您有帮助，请给个 ⭐ Star 支持一下！**

[![Star History Chart](https://api.star-history.com/svg?repos=WizisCool/98tang-autosign&type=Date)](https://star-history.com/#WizisCool/98tang-autosign&Date)

---

*Develop by WizisCool*

</div>