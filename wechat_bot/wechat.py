"""
WeChat Bot for macOS - 微信自动发消息机器人
"""

import os
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
        logging.info(f"检测到WeChat进程，返回码：{result.returncode}，输出：{result.stdout.decode().strip()}")

        # """
        # 检查微信是否已登录
        # """
        # script = '''
        # tell application "System Events"
        #     if not (exists window 1 of process "WeChat") then
        #         return false
        #     end if
        #     tell process "WeChat"
        #         try
        #             -- 尝试获取主窗口标题
        #             get title of window 1
        #             return true
        #         on error
        #             return false
        #         end try
        #     end tell
        # end tell
        # '''
        # result = self._run_applescript(script)
        # if result.lower() != "true":
        #     raise WeChatLoginRequiredError("WeChat未登录，请先登录微信")
        # logging.info("WeChat 已登录")
        pass

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
            time.sleep(0.3)  # 减少等待时间: 0.5 -> 0.3
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
            time.sleep(0.1)  # 减少等待: 0.2 -> 0.1
            
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
            
            # 等待窗口切换完成 - 减少等待: 1.0 -> 0.5
            time.sleep(0.5)  
            logging.info(f"已切换到聊天窗口: {chat_name}")
            return True
            
        finally:
            # 恢复原始剪贴板内容
            pyperclip.copy(old_clipboard)

    def send_message(self, message):
        """
        发送消息
        Args:
            message: 要发送的消息内容
        """
        if not message:
            logging.warning("尝试发送空消息，已忽略")
            return
            
        logging.info(f"准备发送消息，长度: {len(message)}")
        # 激活输入窗口
        self._activate_input_area()
            
        # 清空剪贴板并复制消息 - 减少等待: 0.2 -> 0.1
        pyperclip.copy('')
        time.sleep(0.1)
        pyperclip.copy(message)
        
        # 动态等待消息复制到剪贴板，但使用更短的轮询间隔
        timeout = 0.3  # 减少超时: 0.5 -> 0.3
        start_time = time.time()
        while pyperclip.paste() != message:
            if time.time() - start_time > timeout:
                logging.error("消息复制到剪贴板失败")
                raise WeChatError("无法将消息复制到剪贴板")
            time.sleep(0.05)  # 减少轮询间隔: 0.1 -> 0.05
        
        logging.debug("消息已成功复制到剪贴板")
        
        # 计算基于消息长度的延迟时间，但减少基础延迟
        base_delay = 0.1  # 减少基础延迟: 0.2 -> 0.1
        # 对于大消息，限制最大额外延迟时间
        length_factor = min(len(message) / 2000, 1.5)  # 调整系数
        paste_delay = base_delay + length_factor
        
        # 粘贴消息
        script = '''
        tell application "System Events"
            tell process "WeChat"
                keystroke "v" using {command down}
            end tell
        end tell
        '''
        self._run_applescript(script)
        
        # 等待粘贴完成
        time.sleep(paste_delay)
        
        # 发送消息
        script = '''
        tell application "System Events"
            tell process "WeChat"
                keystroke return
            end tell
        end tell
        '''
        self._run_applescript(script)
        
        # 减少等待: 0.5 -> 0.3
        time.sleep(0.3)
        logging.info("消息发送完成")
        
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
                # 使用屏幕大小作为后备方案
                x, y = 0, 0
                width = screen_width
                height = screen_height
            
            # 计算并点击输入框位置
            input_x = x + width // 2
            input_y = y + int(height * 0.9)
            
            if 0 <= input_x < screen_width and 0 <= input_y < screen_height:
                pyautogui.click(input_x, input_y)
                time.sleep(0.1)  # 减少等待: 0.2 -> 0.1
                
                logging.debug("已点击微信输入区域")
            else:
                logging.warning("计算的点击位置超出屏幕范围，尝试Tab方法")
                
            # 不需要额外延迟，直接进入Tab键备份方案
                
        except Exception as e:
            logging.warning(f"使用PyAutoGUI点击输入区域失败: {e}")

        # 作为备份策略，尝试使用Tab键
        logging.debug("尝试使用Tab键切换到输入框")
        script = '''
        tell application "System Events"
            tell process "WeChat"
                key code 53
                delay 0.1
                keystroke tab
            end tell
        end tell
        '''
        try:
            self._run_applescript(script)
            time.sleep(0.1)  # 减少等待: 0.2 -> 0.1
            logging.debug("已使用Tab键尝试切换到输入框")
        except Exception as e:
            logging.warning(f"使用Tab键切换焦点失败: {e}")

class WeChatMessage:
    """微信消息类，用于构造和解析消息"""
    
    def __init__(self, content, sender=None, timestamp=None, is_group=False, group_name=None):
        self.content = content
        self.sender = sender
        self.timestamp = timestamp or time.time()
        self.is_group = is_group
        self.group_name = group_name

    def __str__(self):
        return self.content
