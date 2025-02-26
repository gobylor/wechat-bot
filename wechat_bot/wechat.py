"""
WeChat Bot for macOS - 微信自动发消息机器人
"""

import time
import subprocess
import pyautogui
import pyperclip
import logging

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
        检查微信是否在运行
        """
        logging.info("正在检查微信是否在运行...")
        result = subprocess.run(['pgrep', 'WeChat'], capture_output=True)
        if result.returncode != 0:
            logging.error("未检测到WeChat进程")
            raise WeChatNotRunningError("WeChat未运行，请先启动微信")
        logging.info("检测到WeChat进程")

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
            subprocess.run(['open', '-a', 'WeChat'], check=True)
            time.sleep(0.3) 
            logging.info("微信窗口已激活")
        except subprocess.CalledProcessError as e:
            logging.error(f"激活微信窗口失败: {e}")
            raise WeChatError("激活微信窗口失败")

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
        
        # 保存当前剪贴板内容
        old_clipboard = pyperclip.paste()
        
        try:
            # 使用剪贴板传递中文名称
            pyperclip.copy(chat_name)
            time.sleep(0.1)  
            
            # 首先按下command+F打开搜索
            script = '''
            tell application "System Events"
                tell process "WeChat"
                    keystroke "f" using {command down}
                    delay 0.1
                end tell
            end tell
            '''
            self._run_applescript(script)
            
            # 粘贴搜索内容并按回车
            script = '''
            tell application "System Events"
                tell process "WeChat"
                    keystroke "v" using {command down}
                    delay 1.5  
                    keystroke return
                end tell
            end tell
            '''
            self._run_applescript(script)
            
            # 等待窗口切换完成 
            time.sleep(1.5)  
            logging.info(f"已切换到聊天窗口: {chat_name}")
            return True
            
        finally:
            # 恢复原始剪贴板内容
            pyperclip.copy(old_clipboard)

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
            script = '''
            tell application "System Events"
                tell process "WeChat"
                    keystroke "v" using {command down}
                end tell
            end tell
            '''
            self._run_applescript(script)
            
            # 根据消息长度等待适当时间
            time.sleep(0.3)
            
            # 发送消息
            script = '''
            tell application "System Events"
                tell process "WeChat"
                    keystroke return
                end tell
            end tell
            '''
            self._run_applescript(script)
            
            time.sleep(0.3)
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
            script = '''
            tell application "System Events"
                tell process "WeChat"
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
