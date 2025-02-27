#!/usr/bin/env python3
import sys
import logging
from pathlib import Path
import shutil

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from wechat_bot import WeChatMac
from wechat_bot.batch_sender import BatchMessageSender

def ensure_config_exists():
    """确保配置文件存在"""
    config_dir = Path(__file__).parent.parent / 'configs'
    config_file = config_dir / 'message_config.yaml'
    
    if not config_file.exists():
        raise FileNotFoundError("配置文件和示例配置文件都不存在")

def main():
    # 设置日志级别
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 确保配置文件存在
        ensure_config_exists()
        
        # 初始化 WeChat 实例
        wechat = WeChatMac()
        
        # 创建批量发送器
        sender = BatchMessageSender(wechat)
        
        # 获取配置文件路径
        config_path = Path(__file__).parent.parent / 'configs' / 'message_config.yaml'
        
        # 发送消息并获取结果
        results = sender.batch_send(config_path)
        
        # 打印发送结果
        for route, recipients in results.items():
            print(f"\n消息路由: {route}")
            for recipient, success in recipients.items():
                status = "成功" if success else "失败"
                print(f"  接收者 {recipient}: {status}")
                
    except FileNotFoundError as e:
        logging.error(f"配置文件错误: {e}")
    except Exception as e:
        logging.error(f"发送消息时出错: {e}")

if __name__ == "__main__":
    main()
