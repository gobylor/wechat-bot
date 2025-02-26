#!/usr/bin/env python3
import sys
import os
import logging
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from wechat_bot import WeChatMac, WeChatError, WeChatNotRunningError, WeChatLoginRequiredError, WeChatPermissionError

def main():
    # 设置日志级别为 DEBUG
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 初始化微信机器人
        bot = WeChatMac()
        
        # 示例：发送消息
        recipients = ["File Transfer"]
        message = "Hello World!"
        results = bot.send_messages_to_recipients(message, recipients)
        
        # 打印发送结果
        for recipient, success in results.items():
            status = "成功" if success else "失败"
            print(f"发送给 {recipient}: {status}")
            
    except WeChatPermissionError as e:
        logging.error(f"权限错误: {e}")
        sys.exit(1)
    except WeChatNotRunningError as e:
        logging.error(f"微信未运行: {e}")
        sys.exit(1)
    except WeChatLoginRequiredError as e:
        logging.error(f"微信未登录: {e}")
        sys.exit(1)
    except WeChatError as e:
        logging.error(f"其他错误: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"未知错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
