"""
WeChat Bot - A Python package for WeChat automation on macOS
支持中英文系统界面
"""

__version__ = "0.1.0"

# 导入主要类，方便使用
from .wechat import WeChatMac, WeChatError, WeChatNotRunningError, WeChatLoginRequiredError, WeChatPermissionError

__all__ = [
    'WeChatMac',
    'WeChatError',
    'WeChatNotRunningError',
    'WeChatLoginRequiredError',
    'WeChatPermissionError'
]
