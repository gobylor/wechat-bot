import yaml
import logging
from pathlib import Path
from typing import Dict, List, Union, Set

from .wechat import WeChatMac

class BatchMessageSender:
    def __init__(self, wechat: WeChatMac):
        self.wechat = wechat
        self.logger = logging.getLogger(__name__)
        self.config_path = None

    def load_config(self, config_path: Union[str, Path]) -> Dict:
        """加载消息配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate_message(self, message: Dict) -> bool:
        """验证消息格式是否正确"""
        if 'type' not in message:
            return False
        
        if message['type'] not in ['text', 'image']:
            return False
            
        if message['type'] == 'text' and 'content' not in message:
            return False
            
        if message['type'] == 'image':
            if 'source' not in message:
                return False
            if message['source'] not in ['file']:
                return False
            if message['source'] == 'file' and 'path' not in message:
                return False
            
        return True

    def validate_config(self, config: Dict) -> bool:
        """验证配置文件格式是否正确"""
        if not all(key in config for key in ['groups', 'messages']):
            return False

        # 验证群组配置
        for group_name, group_config in config['groups'].items():
            if not all(key in group_config for key in ['tags', 'recipients']):
                return False
            if not isinstance(group_config['tags'], list):
                return False
            if not isinstance(group_config['recipients'], list):
                return False

        # 验证消息配置
        for message_name, message_config in config['messages'].items():
            if not all(key in message_config for key in ['tags', 'content']):
                return False
            if not isinstance(message_config['tags'], list):
                return False
            if not isinstance(message_config['content'], list):
                return False
            # 验证黑名单标签格式
            if 'blacklist_tags' in message_config and not isinstance(message_config['blacklist_tags'], list):
                return False
            for message in message_config['content']:
                if not self.validate_message(message):
                    return False

        return True

    def tags_match(self, message_tags: List[str], group_tags: List[str], message_blacklist_tags: List[str] = None) -> bool:
        """判断消息标签是否与群组标签匹配
        
        Args:
            message_tags: 消息标签列表
            group_tags: 群组标签列表
            message_blacklist_tags: 消息黑名单标签列表，默认为None
            
        Returns:
            bool: 如果消息标签与群组标签有交集且群组标签与消息黑名单标签无交集，返回True；否则返回False
        """
        message_tags_set = set(message_tags)
        group_tags_set = set(group_tags)
        
        # 检查群组标签是否与消息黑名单标签有交集
        if message_blacklist_tags:
            blacklist_tags_set = set(message_blacklist_tags)
            if group_tags_set & blacklist_tags_set:
                return False
                
        # 检查消息标签是否与群组标签有交集
        return bool(message_tags_set & group_tags_set)

    def send_message(self, message: Dict, recipients: List[str]) -> Dict[str, bool]:
        """发送单条消息到指定接收者"""
        if not self.validate_message(message):
            self.logger.error(f"Invalid message format: {message}")
            return {recipient: False for recipient in recipients}

        try:
            if message['type'] == 'text':
                return self.wechat.send_messages_to_recipients(
                    message['content'], 
                    recipients
                )
            elif message['type'] == 'image':
                if message['source'] == 'clipboard':
                    return self.wechat.send_clipboard_to_recipients(recipients)
                else:  # source == 'file'
                    image_path = Path(message['path'])
                    if not image_path.is_absolute():
                        config_dir = Path(self.config_path).parent
                        image_path = config_dir / image_path
                    
                    return self.wechat.send_image_to_recipients(
                        str(image_path),
                        recipients
                    )
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return {recipient: False for recipient in recipients}

    def batch_send(self, config_path: Union[str, Path]) -> Dict[str, Dict[str, bool]]:
        """批量发送消息"""
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            self.logger.error(f"Config file not found: {config_path}")
            return {}

        try:
            config = self.load_config(config_path)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {}

        if not self.validate_config(config):
            self.logger.error("Invalid config format")
            return {}

        results = {}

        # 遍历所有消息
        for message_name, message_config in config['messages'].items():
            message_results = {}
            message_tags = message_config['tags']
            # 获取消息的黑名单标签，如果没有设置则为空列表
            message_blacklist_tags = message_config.get('blacklist_tags', [])
            
            for group_name, group_config in config['groups'].items():
                # 判断标签是否匹配，同时考虑黑名单标签
                if self.tags_match(message_tags, group_config['tags'], message_blacklist_tags):
                    for message in message_config['content']:
                        result = self.send_message(message, group_config['recipients'])
                        message_results.update(result)
                        
            results[message_name] = message_results
            
        return results
