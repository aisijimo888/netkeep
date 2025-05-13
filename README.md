# NetKeep

NetKeep是一个自动化工具，用于定期登录和续期各种网站账号，防止账号因长时间不活跃而被删除。

> **重要提示**：当你fork本仓库后，GitHub Actions工作流默认是禁用的。请务必按照[使用GitHub Actions自动运行](#方法2使用github-actions自动运行)部分的说明启用工作流！

## 功能特点

- 🔄 自动登录多个网站账号
- ⏱️ 自动续期需要续期的服务
- 🔔 支持Telegram通知（可选）
- 🔧 灵活的配置选项
- 🚀 可在GitHub Actions中自动运行

## 快速开始

### 方法1：本地运行

1. 克隆仓库
   ```bash
   git clone https://github.com/mqiancheng/netkeep.git
   cd netkeep
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

3. 创建配置文件
   - 创建`config.json`文件
   - 按照下方[配置说明](#配置说明)添加你的账号信息

4. 运行脚本
   ```bash
   python netkeep.py
   ```

### 方法2：使用GitHub Actions自动运行

1. Fork本仓库（建议设为私有仓库以保护账号信息）

2. 设置GitHub Secrets或Variables
   - 在仓库页面，点击`Settings` > `Secrets and variables` > `Actions`
   - 添加`NETKEEP_ACCOUNTS`变量，值为你的账号配置（JSON格式）
   - 如需Telegram通知，添加`TELEGRAM_BOT_TOKEN`和`TELEGRAM_CHAT_ID`

3. 启用GitHub Actions（重要！）
   - 当你fork仓库后，工作流默认是禁用的
   - 在仓库页面，点击`Actions`标签
   - 你会看到一条提示信息："Workflows aren't being run on this forked repository"
   - 点击`I understand my workflows, go ahead and enable them`按钮
   - 然后在工作流列表中找到`NetKeep自动登录`
   - 点击它，然后点击`Enable workflow`按钮

4. 手动触发或等待定时触发
   - 工作流默认每48小时（UTC时间0点）自动运行
   - 也可以在Actions页面手动触发

## 配置说明

### 账号配置格式

```json
[
  {
    "site": "https://example.com",
    "loginApi": "/login",
    "renewApi": "/server/renew/123",
    "username": "your_username",
    "password": "your_password"
  },
  {
    "site": "https://another-site.com",
    "loginApi": "/login",
    "username": "another_username",
    "password": "another_password"
  }
]
```

### 配置项说明

- `site`: 网站地址
- `loginApi`: 登录API路径，通常是"/login"
- `renewApi`: 续期API路径（可选，如不需要续期则省略）
- `username`: 用户名
- `password`: 密码

### 如何获取loginApi和renewApi

获取loginApi和renewApi需要一些网页分析技巧，这里提供一般性指导：

1. **loginApi获取方法**：
   - 打开网站登录页面
   - 右键点击 -> 检查（或按F12打开开发者工具）
   - 在登录表单上找到`action`属性，或者
   - 在Network标签页中找到登录请求的URL路径

2. **renewApi获取方法**：
   - 登录网站后，导航到续期页面
   - 打开开发者工具的Network标签页
   - 点击续期按钮，观察发送的请求
   - 找到续期请求的URL路径

**注意**：每个网站的API路径可能不同，需要根据具体网站自行分析。如果不确定，可以尝试使用浏览器的开发者工具分析网络请求，或查看网站的API文档（如果有）。

### Telegram通知配置

1. 创建Telegram机器人，获取`BOT_TOKEN`
   - 与@BotFather聊天，使用`/newbot`命令创建机器人
   - 记下获得的token

2. 获取`CHAT_ID`
   - 与@userinfobot聊天，获取你的chat_id
   - 或者创建一个群组，将机器人添加为管理员，获取群组chat_id

3. 在`.env`文件或GitHub Secrets中设置：
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

## 安全建议

1. **使用私有仓库**：强烈建议将fork的仓库设为私有，以保护账号信息
2. **定期更新密码**：定期更改网站密码，并更新配置
3. **最小权限原则**：使用专门为自动登录创建的账号，避免使用主账号
4. **监控运行日志**：定期检查GitHub Actions运行日志，确保脚本正常工作

## 常见问题

**Q: 脚本无法登录某些网站怎么办？**
A: 某些网站可能有额外的安全措施。请检查网站是否有验证码或其他安全机制。

**Q: 如何修改自动运行的频率？**
A: 编辑`.github/workflows/netkeep.yml`文件中的`cron`表达式。当前设置为每48小时运行一次（`0 0 */2 * *`）。

**Q: 可以同时登录多少个网站？**
A: 理论上没有限制，但建议根据GitHub Actions的运行时间限制合理设置。

## 贡献指南

欢迎提交Pull Request或Issue来改进这个项目！

## 许可证

MIT License
