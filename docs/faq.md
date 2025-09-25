# 故障排除

## 常见问题

### Q: Github Actions运行失败怎么办？
A: 检查以下几点：
1. 确保已正确配置 `SITE_USERNAME` 和 `SITE_PASSWORD`
2. 检查账号密码是否正确
3. 查看Actions日志了解具体错误信息
4. 确保仓库已启用Actions功能
5. 如果使用Environment Secrets，确保 `98tang-autosign` 环境已正确创建和配置

### Q: Environment Secrets和Repository Secrets有什么区别？
A: 
- **Environment Secrets (推荐)**: 
  - 更高的安全性，可以设置环境保护规则
  - 支持审批流程和部署保护
  - 便于管理多环境配置
- **Repository Secrets (兼容)**:
  - 配置简单，直接在仓库设置中添加
  - 适合简单的单一环境使用
  - 系统会自动回退到此模式

### Q: 如何知道当前使用的是哪种配置模式？
A: 查看Actions运行日志：
- ✅ "Environment secrets模式: 98tang-autosign" - 使用环境配置
- ⚠️ "Repository secrets模式 - 回退模式" - 使用仓库配置

### Q: 98tang-autosign环境创建失败或无法访问？
A: 可能的解决方案：
1. 确保在正确的仓库中创建环境
2. 检查环境名称是否完全匹配：`98tang-autosign`
3. 确保已在环境中添加必需的secrets
4. 如果仍有问题，系统会自动回退到Repository Secrets模式

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

### Q: 程序运行缓慢或超时？
A: 可以调整以下参数：
```env
TIMING_MULTIPLIER=0.8     # 减小延时倍数
TIMEOUT_MINUTES=10        # 增加超时时间
ENABLE_SMART_TIMING=false # 关闭智能延时
```

### Q: 签到成功但没有积分？
A: 可能的原因：
1. 当天已经签到过了
2. 网站规则变化
3. 账号状态异常
4. 检查程序日志确认签到状态

### Q: workflow只能在main分支运行吗？
A: 不是的，分支运行规则如下：
- **定时任务 (schedule)**: 只在默认分支（通常是main）上运行
- **手动触发 (workflow_dispatch)**: 可以在任何分支上运行
- **推送触发 (push)**: 可以配置在指定分支上运行
- **PR触发 (pull_request)**: 可以配置在PR目标分支上运行

如果你想在develop分支测试，可以：
1. 切换到develop分支
2. 在GitHub Actions页面手动触发workflow
3. 或者推送代码到develop分支（如果配置了push触发器）

### Q: GitHub Actions显示"配置文件不存在: config.env"错误？
A: 这是因为程序在CI环境中仍然检查配置文件。解决方案：

**方法1：推荐 - 升级到最新版本**
最新版本已经修复了这个问题，会自动检测CI环境并跳过配置文件检查。

**方法2：临时解决**
确保你的GitHub Actions环境变量已正确设置：
- 使用Environment secrets（推荐）或Repository secrets
- 必须设置 `SITE_USERNAME` 和 `SITE_PASSWORD`
- 确保secrets名称完全匹配

**方法3：手动修复**
如果使用旧版本，在 `main.py` 中添加CI环境检测。

### Q: 如何调试程序？
A: 本地运行时设置：
```env
HEADLESS=false     # 显示浏览器窗口
LOG_LEVEL=DEBUG    # 显示详细日志
```

## 日志分析

### 常见错误信息

**登录失败**
```
Error: Login failed - Invalid credentials
```
解决方案：检查用户名和密码是否正确

**元素找不到**
```
Error: Element not found - xpath: //button[@id='signin']
```
解决方案：网站可能更新了页面结构，需要更新代码

**网络超时**
```
Error: Timeout waiting for page to load
```
解决方案：检查网络连接，或增加 `TIMEOUT_MINUTES` 参数

**安全验证失败**
```
Error: Security question verification failed
```
解决方案：检查 `SECURITY_QUESTION` 和 `SECURITY_ANSWER` 配置

### 日志级别说明

- **DEBUG**: 显示所有调试信息，包括页面元素查找过程
- **INFO**: 显示基本操作信息，如登录、签到状态
- **WARNING**: 显示警告信息，如重试操作
- **ERROR**: 只显示错误信息

## 获取帮助

如果遇到无法解决的问题：

1. **查看日志文件**: 在 `logs/` 目录下查看详细日志
2. **提交Issue**: 在GitHub仓库提交Issue，包含：
   - 详细的问题描述
   - 相关的日志信息
   - 系统环境信息
   - 复现步骤
3. **检查更新**: 确保使用的是最新版本的代码
