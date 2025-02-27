# WeChat Bot - 安全稳定的微信机器人

基于 Python 和 AppleScript 的 macOS 微信自动化工具，采用模拟人工操作的方式，安全可靠，不会导致封号。

## 目录

- [WeChat Bot - 安全稳定的微信机器人](#wechat-bot---安全稳定的微信机器人)
  - [目录](#目录)
  - [功能特点](#功能特点)
  - [环境要求](#环境要求)
  - [快速开始](#快速开始)
  - [详细使用指南](#详细使用指南)
    - [基础功能](#基础功能)
    - [批量发送消息](#批量发送消息)
    - [常见问题](#常见问题)
  - [安全说明](#安全说明)
  - [许可证](#许可证)

## 功能特点

- 🔒 安全可靠：模拟人工操作，不调用微信内部接口
- 💬 消息功能：支持发送文本、图片、文件等多种类型消息
- 📦 批量发送：支持基于标签的消息路由，轻松管理群发
- 🔄 自动重试：内置智能重试机制，提高发送成功率
- 📱 多显示器支持：完美适配多屏环境
- 📝 日志完善：详细的日志记录，方便排查问题

## 环境要求

- macOS 10.15 或更高版本
- Python 3.7+
- 微信 Mac 版本
- [可选] pip 包管理工具

## 快速开始

1. **安装准备**
   ```bash
   # 克隆仓库
   git clone https://github.com/yourusername/wechat-bot.git
   cd wechat-bot

   # 安装依赖
   pip install -r requirements.txt
   ```

2. **系统权限设置**
   - 打开系统偏好设置 > 安全性与隐私 > 隐私
   - 允许终端和 Python 访问：
     - 辅助功能
     - 屏幕录制
     - 自动化

3. **运行示例**
   ```python
   from wechat_bot import WeChatMac

   # 初始化微信机器人
   wechat = WeChatMac()

   # 发送简单消息
   wechat.find_chat("文件传输助手")  # 先找到聊天窗口
   wechat.send_message("Hello World!")  # 发送消息
   ```

## 详细使用指南

### 基础功能

1. **发送文本消息**
   ```python
   wechat.find_chat("群聊名称")
   wechat.send_message("这是一条测试消息")
   ```

2. **发送图片**
   ```python
   wechat.send_image("/path/to/image.jpg")
   ```

3. **发送文件**
   ```python
   wechat.send_file("/path/to/file.pdf")
   ```

### 批量发送消息

1. **配置文件设置** (`configs/message_config.yaml`)
   ```yaml
   groups:
     tech_group:
       tags: ["tech"]
       recipients:
         - "技术交流群"
         - "开发群"
   
   messages:
     tech_update:
       tags: ["tech"]
       content:
         - type: text
           content: "技术更新通知"
   ```

2. **使用批量发送**
   ```python
   from wechat_bot import WeChatMac
   from wechat_bot.batch_sender import BatchMessageSender

   wechat = WeChatMac()
   sender = BatchMessageSender(wechat)
   sender.batch_send('configs/message_config.yaml')
   ```

### 常见问题

1. **找不到聊天窗口？**
   - 检查聊天名称是否正确

2. **发送消息失败？**
   - 检查是否已授予所有必要的系统权限
   - 确保微信已登录且网络正常
   - 查看日志获取详细错误信息

## 安全说明

本工具采用模拟人工操作的方式进行自动化，主要特点：

- ✅ 不调用微信内部接口
- ✅ 不破解或修改微信程序
- ✅ 不截取或存储用户数据
- ✅ 内置多重安全保护机制

建议：
- 合理控制消息发送频率
- 避免短时间内大量重复操作
- 定期检查微信官方政策更新

## 许可证

MIT License