# WeChat Bot - 安全稳定的微信机器人

基于 Python 和 AppleScript 的 macOS 微信自动化工具，采用模拟人工操作的方式，安全可靠，不会导致封号。

## 为什么选择这个机器人？

- 专为 macOS 设计和优化
- 采用模拟人工操作方式，不调用微信内部接口，安全性高
- 使用 AppleScript 和键盘快捷键混合控制，稳定可靠
- 内置多重安全保护机制，预防封号风险
- 完善的错误处理和日志记录，便于排查问题

## 功能特点

- 自动查找并进入聊天
- 发送文本消息和结构化消息
- 发送文件
- 删除消息
- 多显示器支持
- 自动重试机制
- 混合使用 AppleScript 和键盘快捷键，提高稳定性
- 完善的错误处理和日志记录

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/wechat-bot.git
cd wechat-bot
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用示例

### 基础使用
```python
from wechat_bot.wechat import WeChatMac

# 初始化微信机器人
wechat = WeChatMac()

# 查找并进入聊天
wechat.find_chat("File Transfer")

# 发送消息
wechat.send_message("Hello from WeChat Bot!")
```

## 注意事项

1. 使用前请确保微信已经登录
2. 首次运行时需要授予必要的系统权限

## 许可证

MIT License