# 贡献指南

欢迎提交Issue和Pull Request！

## 提交Issue

使用清晰的标题描述问题，并提供以下信息：

### Bug报告
- **问题描述**: 详细描述遇到的问题
- **复现步骤**: 提供完整的复现步骤
- **期望行为**: 说明期望的正确行为
- **实际行为**: 说明实际发生的情况
- **环境信息**: 
  - 操作系统版本
  - Python版本
  - Chrome版本
  - 运行方式（本地/Github Actions）
- **日志信息**: 附上相关的错误日志

### 功能请求
- **功能描述**: 详细描述希望添加的功能
- **使用场景**: 说明该功能的使用场景
- **实现建议**: 如果有实现思路可以一并提供

## 提交代码

### 开发环境搭建

1. Fork本仓库到你的GitHub账号
2. 克隆你的Fork仓库到本地：
   ```bash
   git clone https://github.com/your-username/98tang-autosign.git
   cd 98tang-autosign
   ```
3. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 开发流程

1. **创建特性分支**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **编写代码**:
   - 遵循现有的代码风格
   - 添加必要的注释
   - 确保代码可读性

3. **测试代码**:
   ```bash
   # 本地测试
   python main.py
   ```
   
   **GitHub Actions测试**:
   - 如果修改了workflow文件，建议创建测试用的environment进行验证
   - 可以使用 `workflow_dispatch` 手动触发测试
   - 确保新功能在云端环境中也能正常工作

4. **提交更改**:
   ```bash
   git add .
   git commit -m "Add new feature: 功能描述"
   ```

5. **推送分支**:
   ```bash
   git push origin feature/new-feature
   ```

6. **创建Pull Request**:
   - 在GitHub上创建Pull Request
   - 详细描述修改内容
   - 说明测试情况

### 代码规范

#### Python代码风格
- 使用4个空格缩进
- 函数和类名使用有意义的命名
- 添加必要的文档字符串
- 遵循PEP 8规范

#### 提交信息规范
```
类型: 简短描述

详细描述（可选）

- 修改点1
- 修改点2
```

类型包括：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 代码审查

Pull Request将经过以下审查：

1. **代码质量**: 检查代码风格和最佳实践
2. **功能测试**: 验证新功能是否正常工作
3. **兼容性**: 确保不会破坏现有功能
4. **文档**: 检查是否需要更新相关文档

## 项目架构

### 目录结构
```
src/
├── core/           # 核心功能
├── browser/        # 浏览器操作
├── automation/     # 自动化逻辑
├── notifications/  # 通知模块
└── utils/          # 工具函数
```

### 主要模块说明

- **core/app.py**: 主应用逻辑
- **core/config.py**: 配置管理
- **core/logger.py**: 日志系统
- **browser/driver.py**: 浏览器驱动管理
- **automation/signin.py**: 签到核心逻辑
- **notifications/telegram.py**: Telegram通知
- **utils/screenshot_helper.py**: 页面截图功能

### 添加新功能

1. **确定模块位置**: 根据功能类型选择合适的模块
2. **保持接口一致**: 遵循现有的接口设计模式
3. **添加配置项**: 在config.py中添加相关配置
4. **更新文档**: 在docs/中更新相关文档
5. **添加日志**: 使用统一的日志系统记录操作

### 技术实现说明

#### 截图功能架构
- **utils/screenshot_helper.py**: 封装截图逻辑
  - 支持错误页面和成功页面截图
  - 自动调整页面大小以获得完整截图
  - 集成Telegram文件发送功能
  - 支持配置化控制截图行为

- **集成点**: 
  - 错误处理: `app.py`的`_send_error_with_log`方法
  - 成功通知: `app.py`的`_send_execution_summary`方法
  - 配置管理: `config.py`的`TELEGRAM_SEND_SCREENSHOT`选项

#### 添加新通知类型
1. 在`notifications/telegram.py`中扩展方法
2. 在`utils/`目录下创建相应的辅助类
3. 在`config.py`中添加控制开关
4. 在主应用逻辑中集成调用

## 许可证

本项目采用 [MIT许可证](../LICENSE)。提交代码即表示同意将代码以MIT许可证开源。
