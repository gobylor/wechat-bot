"""
WeChat Bot for macOS - 微信自动发消息机器人
"""

from math import log
import time
import subprocess
import pyautogui
import pyperclip
import logging
import datetime

class WeChatError(Exception):
    """微信机器人异常基类"""
    pass

class WeChatNotRunningError(WeChatError):
    """微信未运行异常"""
    pass

class WeChatLoginRequiredError(WeChatError):
    """微信未登录异常"""
    pass

class WeChatPermissionError(WeChatError):
    """权限不足异常"""
    pass

class WeChatMac:
    """macOS 版微信自动化操作类"""

    def __init__(self):
        """
        初始化微信机器人
        """
        logging.info("初始化 WeChatMac 实例")
        self.process_name = None  # 存储检测到的进程名称
        # 初始化时进行所有必要的检查
        self._check_permissions()
        self._check_wechat_running()
        logging.info("WeChatMac 实例初始化完成")
    
    def _check_permissions(self):
        """
        检查必要的系统权限
        1. 屏幕录制权限 (通过 pyautogui)
        2. 辅助功能权限 (通过 AppleScript)
        """
        try:
            # 检查屏幕录制权限
            pyautogui.screenshot()
            logging.debug("屏幕录制权限检查通过")
            
            # 检查辅助功能权限
            test_script = '''
            tell application "System Events"
                return true
            end tell
            '''
            self._run_applescript(test_script)
            logging.debug("辅助功能权限检查通过")
        except Exception as e:
            logging.error("缺少必要的系统权限")
            raise WeChatPermissionError(
                "缺少必要的系统权限。请在系统设置中授予以下权限：\n"
                "1. 屏幕录制权限\n"
                "2. 辅助功能权限"
            )

    def _check_wechat_running(self):
        """
        检查微信是否在运行，同时检查英文版和中文版
        """
        logging.info("正在检查微信是否在运行...")
        
        # 检查英文版微信进程
        result_en = subprocess.run(['pgrep', 'WeChat'], capture_output=True)
        if result_en.returncode == 0:
            self.process_name = "WeChat"
            logging.info("检测到英文版WeChat进程")
            return
            
        # 检查中文版微信进程
        result_cn = subprocess.run(['pgrep', '微信'], capture_output=True)
        if result_cn.returncode == 0:
            self.process_name = "微信"
            logging.info("检测到中文版微信进程")
            return
            
        # 如果两种进程都未检测到，则抛出异常
        logging.error("未检测到WeChat或微信进程")
        raise WeChatNotRunningError("WeChat/微信未运行，请先启动微信")

    def _run_applescript(self, script):
        """
        执行AppleScript脚本
        """
        logging.debug(f"执行AppleScript脚本: {script}")
        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if result.returncode != 0:
                logging.error(f"AppleScript执行失败: {result.stderr}")
                raise WeChatError(f"AppleScript执行失败: {result.stderr}")
            logging.debug(f"AppleScript执行成功，输出: {result.stdout.strip()}")
            return result.stdout.strip()
        except Exception as e:
            logging.error(f"执行AppleScript时发生错误: {str(e)}")
            raise WeChatError(f"执行AppleScript时发生错误: {str(e)}")

    def activate_window(self):
        """
        激活微信窗口
        """
        logging.info("正在激活微信窗口")
        try:
            # 使用进程名打开应用
            app_name = "WeChat" if self.process_name == "WeChat" else "微信"
            subprocess.run(['open', '-a', app_name], check=True)
            time.sleep(0.3) 
            logging.info("微信窗口已激活")
        except subprocess.CalledProcessError as e:
            logging.error(f"激活微信窗口失败: {e}")
            raise WeChatError("激活微信窗口失败")

    def _send_keystroke(self, key, modifiers=None, delay=0.1):
        """
        发送键盘按键
        
        Args:
            key (str): 要发送的键
            modifiers (dict): 修饰键，例如 {"command down"}
            delay (float): 执行后等待的时间
        
        Returns:
            bool: 是否成功执行
        """
        try:
            modifiers_str = " using {" + ", ".join(modifiers) + "}" if modifiers else ""
            script = f'''
            tell application "System Events"
                tell process "{self.process_name}"
                    keystroke "{key}"{modifiers_str}
                end tell
            end tell
            '''
            self._run_applescript(script)
            if delay > 0:
                time.sleep(delay)
            return True
        except Exception as e:
            logging.error(f"发送按键 {key} 失败: {str(e)}")
            return False

    def _send_key(self, key, modifiers=None, delay=0.1):
        """
        发送特殊键（如回车、Tab等）
        这与_send_keystroke不同，它使用'key code'而不是'keystroke'
        
        Args:
            key (int or str): 要发送的键的键码或名称
            modifiers (list): 修饰键列表，例如 ["command down"]
            delay (float): 执行后等待的时间
        
        Returns:
            bool: 是否成功执行
        """
        try:
            # 如果key是字符串名称，则转换为对应的键码
            key_code = key
            if isinstance(key, str):
                key_map = {
                    "return": 36,
                    "tab": 48,
                    "space": 49,
                    "delete": 51,
                    "escape": 53,
                    "left": 123,
                    "right": 124,
                    "down": 125,
                    "up": 126
                }
                key_code = key_map.get(key.lower(), key)
            
            modifiers_str = " using {" + ", ".join(modifiers) + "}" if modifiers else ""
            script = f'''
            tell application "System Events"
                tell process "{self.process_name}"
                    key code {key_code}{modifiers_str}
                end tell
            end tell
            '''
            self._run_applescript(script)
            if delay > 0:
                time.sleep(delay)
            return True
        except Exception as e:
            logging.error(f"发送键 {key} 失败: {str(e)}")
            return False

    def _cmd_keystroke(self, key, delay=0.1):
        """Command + 按键的快捷方式"""
        return self._send_keystroke(key, ["command down"], delay)

    def _paste(self, delay=0.3):
        """执行粘贴操作 (Command+V)"""
        return self._cmd_keystroke("v", delay)

    def _press_return(self, delay=0.3):
        """
        按下回车键 - 使用key code确保按下的是真正的回车键
        而不是输入"return"文本
        """
        return self._send_key("return", delay=delay)

    def _search_contact(self, contact_name):
        """
        使用搜索功能查找联系人
        
        Args:
            contact_name (str): 联系人名称
            
        Returns:
            bool: 是否成功搜索
        """
        # 保存当前剪贴板内容
        old_clipboard = self._get_clipboard_content()
        
        try:
            # 复制联系人名称到剪贴板
            pyperclip.copy(contact_name)
            time.sleep(0.1)
            
            # 打开搜索 (Command+F)
            if not self._cmd_keystroke("f", 0.1):
                return False
                
            # 粘贴搜索内容
            if not self._paste(1.5):
                return False
                
            # 按回车确认搜索 - 使用修改后的方法确保按下真正的回车键
            if not self._press_return(0.5):
                return False
                
            return True
        finally:
            # 恢复剪贴板内容
            self._set_clipboard_content(old_clipboard)
    
    def find_chat(self, chat_name):
        """
        查找并切换到指定聊天窗口
        Args:
            chat_name: 聊天窗口名称
        Returns:
            bool: 是否成功找到并切换到聊天窗口
        """
        if not chat_name:
            logging.error("未指定聊天窗口名称")
            raise WeChatError("未指定聊天窗口名称")
        
        logging.info(f"尝试查找并切换到聊天窗口: {chat_name}")
        # 确保窗口处于激活状态
        self.activate_window()
        
        # 使用封装的搜索方法
        success = self._search_contact(chat_name)
        
        if success:
            logging.info(f"已切换到聊天窗口: {chat_name}")
        else:
            logging.error(f"无法切换到聊天窗口: {chat_name}")
            
        return success

    def _prepare_message(self, message):
        """
        准备消息发送，将消息复制到剪贴板
        Args:
            message: 要发送的消息内容
        Returns:
            bool: 是否成功准备消息
        """
        if not message:
            logging.warning("尝试发送空消息")
            return False
            
        logging.debug(f"准备发送消息，长度: {len(message)}")
        
        # 清空并设置剪贴板
        pyperclip.copy('')
        time.sleep(0.1)
        pyperclip.copy(message)
        
        # 验证消息是否成功复制到剪贴板
        timeout = 0.3
        start_time = time.time()
        while pyperclip.paste() != message:
            if time.time() - start_time > timeout:
                logging.error("消息复制到剪贴板失败")
                return False
            time.sleep(0.05)
        
        logging.debug("消息已成功复制到剪贴板")
        return True

    def _paste_and_send(self):
        """
        执行消息的粘贴和发送操作
        Returns:
            bool: 是否成功发送消息
        """
        try:
            # 激活输入区域
            self._activate_input_area()
            
            # 粘贴消息
            if not self._paste(0.3):
                return False
            
            # 发送消息 
            if not self._press_return(0.3):
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"发送消息时发生错误: {str(e)}")
            return False

    def send_message(self, message):
        """
        发送消息
        Args:
            message: 要发送的消息内容
        Returns:
            bool: 是否成功发送消息
        """
        if not self._prepare_message(message):
            return False
            
        return self._paste_and_send()

    def send_messages_to_recipients(self, message, recipients):
        """
        批量发送消息给多个接收者
        Args:
            message: 要发送的消息内容
            recipients: 接收者列表，每个元素为聊天窗口名称
        Returns:
            dict: 每个接收者的发送状态，格式为 {recipient: success_status}
        """
        if not message or not recipients:
            logging.warning("消息内容或接收者列表为空")
            return {}
            
        logging.info(f"准备向 {len(recipients)} 个接收者发送消息")
        results = {}
        
        # 预先准备消息，避免重复操作
        if not self._prepare_message(message):
            return {recipient: False for recipient in recipients}
        
        for recipient in recipients:
            try:
                logging.info(f"正在发送消息给: {recipient}")
                if self.find_chat(recipient):
                    success = self._paste_and_send()
                    results[recipient] = success
                    log_level = logging.INFO if success else logging.ERROR
                    logging.log(log_level, f"发送消息给 {recipient}: {'成功' if success else '失败'}")
                else:
                    results[recipient] = False
                    logging.error(f"未找到聊天窗口: {recipient}")
            except Exception as e:
                results[recipient] = False
                logging.error(f"发送消息给 {recipient} 时发生错误: {str(e)}")
        
        # 统计发送结果
        success_count = sum(1 for status in results.values() if status)
        logging.info(f"批量发送完成。成功: {success_count}/{len(recipients)}")
        return results

    def _get_clipboard_content(self):
        """
        获取当前剪贴板内容，支持文本和非文本内容
        
        Returns:
            tuple: (content_type, content) where content_type is 'text', 'image', 'file' or None
        """
        try:
            import AppKit
            pasteboard = AppKit.NSPasteboard.generalPasteboard()
            types = pasteboard.types()
            logging.debug(f"剪贴板类型: {types}")
            
            if AppKit.NSPasteboardTypeString in types:
                text = pasteboard.stringForType_(AppKit.NSPasteboardTypeString)
                logging.debug(f"从剪贴板获取文本内容: {text[:20]}...")
                return ('text', text)
            elif AppKit.NSPasteboardTypeFileURL in types:
                files = pasteboard.propertyListForType_(AppKit.NSPasteboardTypeFileURL)
                if files:
                    logging.debug(f"从剪贴板获取文件内容: {files}")
                    return ('file', files)
                logging.debug("剪贴板不包含文件")
                return None
            elif AppKit.NSPasteboardTypePDF in types:
                return ('pdf', pasteboard.dataForType_(AppKit.NSPasteboardTypePDF))
            elif AppKit.NSPasteboardTypeTIFF in types:
                return ('image', ('tiff', pasteboard.dataForType_(AppKit.NSPasteboardTypeTIFF)))
            elif AppKit.NSPasteboardTypePNG in types:
                return ('image', ('png', pasteboard.dataForType_(AppKit.NSPasteboardTypePNG)))
            else:
                # Handle WeChat specific type
                if "com.tencent.xinWeChat.message" in types:
                    logging.debug("检测到微信消息类型的剪贴板内容")
                    data = pasteboard.dataForType_("com.tencent.xinWeChat.message")
                    if data:
                        return ('wechat_message', data)
                    logging.debug("无法获取微信消息内容")
                logging.error("剪贴板包含其他格式的数据")
                return None
        
        except Exception as e:
            import traceback
            logging.error(f"获取剪贴板内容时发生错误: {str(e)}")
            logging.debug(f"错误详情: {traceback.format_exc()}")
            return None

    def _set_clipboard_content(self, content):
        """
        设置剪贴板内容，支持文本和非文本内容
        
        Args:
            content: (content_type, content) tuple from _get_clipboard_content
        """
        if not content or content[0] is None:
            logging.debug("剪贴板内容为空，不进行设置")
            return
            
        try:
            import AppKit
            pasteboard = AppKit.NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            
            content_type, data = content
            
            if content_type == 'text':
                result = pasteboard.setString_forType_(data, AppKit.NSPasteboardTypeString)
                logging.debug(f"设置剪贴板文本内容: {data[:20]}... 结果: {result}")
            elif content_type == 'pdf':
                result = pasteboard.setData_forType_(data, AppKit.NSPasteboardTypePDF)
                logging.debug(f"设置剪贴板PDF内容 结果: {result}") 
            elif content_type == 'image':
                img_type, img_data = data
                if img_type == 'tiff':
                    result = pasteboard.setData_forType_(img_data, AppKit.NSPasteboardTypeTIFF)
                elif img_type == 'png':
                    result = pasteboard.setData_forType_(img_data, AppKit.NSPasteboardTypePNG)
                else:
                    logging.error(f"不支持的图像格式: {img_type}")
                logging.debug(f"设置剪贴板图片内容({img_type}) 结果: {result}")
            elif content_type == 'file':
                result = pasteboard.setPropertyList_forType_([data], AppKit.NSPasteboardTypeFileURL)
                logging.debug(f"设置剪贴板文件内容: {data} 结果: {result}")
            elif content_type == 'wechat_message':
                result = pasteboard.setData_forType_(data, "com.tencent.xinWeChat.message")
                logging.debug(f"设置剪贴板微信消息内容 结果: {result}")
            else:
                logging.error(f"未知的剪贴板内容类型: {content_type}")
                
        except Exception as e:
            logging.error(f"设置剪贴板内容时出错: {str(e)}")
            # 对于文本内容，尝试使用 pyperclip 作为后备
            if content_type == 'text':
                pyperclip.copy(data)

    def _activate_input_area(self):
        """
        激活聊天窗口中的输入区域
        使用PyAutoGUI点击输入框位置，更加可靠
        """
        logging.debug("正在尝试激活微信输入区域")
        
        try:
            # 确保窗口已激活，减少等待时间
            self.activate_window()
            time.sleep(0.2)  # 减少等待: 0.5 -> 0.2
            
            # 获取屏幕尺寸
            screen_width, screen_height = pyautogui.size()
            
            # 获取窗口信息
            script = f'''
            tell application "System Events"
                tell process "{self.process_name}"
                    set frontWindow to window 1
                    set winPos to position of frontWindow
                    set winSize to size of frontWindow
                    set xPos to item 1 of winPos
                    set yPos to item 2 of winPos
                    set winWidth to item 1 of winSize
                    set winHeight to item 2 of winSize
                    return xPos & "," & yPos & "," & winWidth & "," & winHeight
                end tell
            end tell
            '''
            
            window_info_str = self._run_applescript(script)
            
            # 解析逻辑
            try:
                import re
                numbers = re.findall(r'\d+', window_info_str)
                if len(numbers) >= 4:
                    x = int(numbers[0])
                    y = int(numbers[1])
                    width = int(numbers[2])
                    height = int(numbers[3])
                else:
                    raise ValueError("无法提取足够的数字")
                    
            except (ValueError, IndexError) as e:
                logging.warning(f"解析窗口信息失败: {e}, 使用默认值")
                raise WeChatError("解析窗口信息失败")
            
            # 计算并点击输入框位置
            input_x = x + width // 2
            input_y = y + int(height * 0.9)
            
            if 0 <= input_x < screen_width and 0 <= input_y < screen_height:
                pyautogui.click(input_x, input_y)
                time.sleep(0.1) 
                
                logging.debug("已点击微信输入区域")
            else:
                logging.warning("计算的点击位置超出屏幕范围，尝试Tab方法")
                
        except Exception as e:
            logging.warning(f"使用PyAutoGUI点击输入区域失败: {e}")

    def send_clipboard_content(self):
        """
        直接发送剪贴板内容
        用户提前复制好内容（可以是文本、图片、聊天记录等），然后直接发送
        
        Returns:
            bool: 是否成功发送剪贴板内容
        """
        logging.info("准备发送剪贴板内容")
        
        try:
            # 激活输入区域
            self._activate_input_area()
            time.sleep(0.2)
            
            self._paste(0.5)
            
            # 发送消息
            if not self._press_return(0.3):
                return False
            
            logging.info("剪贴板内容已发送")
            return True
            
        except Exception as e:
            logging.error(f"发送剪贴板内容时发生错误: {str(e)}")
            return False

    def send_clipboard_to_recipients(self, recipients):
        """
        批量发送剪贴板内容给多个接收者
        
        Args:
            recipients: 接收者列表，每个元素为聊天窗口名称
            
        Returns:
            dict: 每个接收者的发送状态，格式为 {recipient: success_status}
        """
        if not recipients:
            logging.warning("接收者列表为空")
            return {}
        
        # 先获取原始剪贴板内容
        original_clipboard = self._get_clipboard_content()
        logging.debug(f"保存原始剪贴板内容类型: {original_clipboard[0] if original_clipboard else 'None'}")
        
        logging.info(f"准备向 {len(recipients)} 个接收者发送剪贴板内容")
        results = {}
        
        for recipient in recipients:
            try:
                logging.info(f"正在发送剪贴板内容给: {recipient}")
                
                # 使用临时文本进行联系人搜索，避免破坏剪贴板中的内容
                temp_text = f"search_{recipient}_{datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}"
                self._set_clipboard_content(('text', temp_text))
                
                if self.find_chat(recipient):
                    # 恢复原始剪贴板内容
                    self._set_clipboard_content(original_clipboard)
                    time.sleep(0.2)  # 给系统一点时间处理剪贴板变化
                    
                    # 发送内容
                    success = self.send_clipboard_content()
                    results[recipient] = success
                    log_level = logging.INFO if success else logging.ERROR
                    logging.log(log_level, f"发送剪贴板内容给 {recipient}: {'成功' if success else '失败'}")
                else:
                    results[recipient] = False
                    logging.error(f"未找到聊天窗口: {recipient}")
            except Exception as e:
                results[recipient] = False
                logging.error(f"发送剪贴板内容给 {recipient} 时发生错误: {str(e)}")
        
        # 统计发送结果
        success_count = sum(1 for status in results.values() if status)
        logging.info(f"批量发送完成。成功: {success_count}/{len(recipients)}")
        return results
