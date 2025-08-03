"""
WebSocket实时聊天模块
"""
import json
import time
import asyncio
import threading
from typing import Dict, List, Callable, Optional
import websocket
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import settings
from utils import log


class WebSocketChatManager:
    """WebSocket聊天管理器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.BROWSER_TIMEOUT)
        self.ws = None
        self.ws_url = None
        self.is_connected = False
        self.message_handlers = []
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = settings.WS_MAX_RECONNECT_ATTEMPTS
        self.reconnect_interval = settings.WS_RECONNECT_INTERVAL
        self.running = False
        
        # 消息队列
        self.message_queue = []
        self.queue_lock = threading.Lock()
    
    def extract_websocket_info(self) -> bool:
        """从页面中提取WebSocket连接信息"""
        try:
            log.info("正在提取WebSocket连接信息...")
            
            # 访问聊天页面
            chat_url = "https://i.zhaopin.com/chat"
            self.driver.get(chat_url)
            time.sleep(3)
            
            # 从页面源码中提取WebSocket URL
            page_source = self.driver.page_source
            
            # 尝试从JavaScript代码中提取WebSocket URL
            import re
            
            # 常见的WebSocket URL模式
            ws_patterns = [
                r'ws://[^"\']+',
                r'wss://[^"\']+',
                r'"wsUrl":\s*"([^"]+)"',
                r'"websocket":\s*"([^"]+)"',
                r'WebSocket\(["\']([^"\']+)["\']',
                r'new\s+WebSocket\(["\']([^"\']+)["\']'
            ]
            
            for pattern in ws_patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    self.ws_url = matches[0]
                    log.info(f"找到WebSocket URL: {self.ws_url}")
                    return True
            
            # 如果没有找到，尝试从网络请求中获取
            return self._extract_from_network_requests()
            
        except Exception as e:
            log.error(f"提取WebSocket信息失败: {e}")
            return False
    
    def _extract_from_network_requests(self) -> bool:
        """从网络请求中提取WebSocket信息"""
        try:
            # 获取浏览器的网络日志
            logs = self.driver.get_log('performance')
            
            for log_entry in logs:
                message = json.loads(log_entry['message'])
                
                if message['message']['method'] == 'Network.webSocketCreated':
                    ws_url = message['message']['params']['url']
                    if 'zhaopin' in ws_url:
                        self.ws_url = ws_url
                        log.info(f"从网络日志中找到WebSocket URL: {ws_url}")
                        return True
            
            return False
            
        except Exception as e:
            log.error(f"从网络请求提取WebSocket信息失败: {e}")
            return False
    
    def connect(self) -> bool:
        """连接WebSocket"""
        try:
            if not self.ws_url:
                if not self.extract_websocket_info():
                    log.error("无法获取WebSocket连接信息")
                    return False
            
            log.info(f"正在连接WebSocket: {self.ws_url}")
            
            # 获取必要的headers和cookies
            headers = self._get_websocket_headers()
            
            # 创建WebSocket连接
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                header=headers,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # 在新线程中运行WebSocket
            self.running = True
            ws_thread = threading.Thread(target=self.ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            # 等待连接建立
            timeout = 10
            start_time = time.time()
            while not self.is_connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            if self.is_connected:
                log.info("WebSocket连接成功")
                return True
            else:
                log.error("WebSocket连接超时")
                return False
                
        except Exception as e:
            log.error(f"WebSocket连接失败: {e}")
            return False
    
    def _get_websocket_headers(self) -> List[str]:
        """获取WebSocket连接所需的headers"""
        try:
            headers = []
            
            # 获取cookies
            cookies = self.driver.get_cookies()
            cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            headers.append(f"Cookie: {cookie_str}")
            
            # 添加其他必要的headers
            headers.extend([
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Origin: https://i.zhaopin.com",
                "Referer: https://i.zhaopin.com/chat"
            ])
            
            return headers
            
        except Exception as e:
            log.error(f"获取WebSocket headers失败: {e}")
            return []
    
    def _on_open(self, ws):
        """WebSocket连接打开回调"""
        log.info("WebSocket连接已打开")
        self.is_connected = True
        self.reconnect_attempts = 0
        
        # 发送心跳包
        self._start_heartbeat()
    
    def _on_message(self, ws, message):
        """WebSocket消息接收回调"""
        try:
            log.debug(f"收到WebSocket消息: {message}")
            
            # 解析消息
            msg_data = json.loads(message)
            
            # 添加到消息队列
            with self.queue_lock:
                self.message_queue.append({
                    'timestamp': time.time(),
                    'data': msg_data,
                    'raw_message': message
                })
            
            # 调用消息处理器
            for handler in self.message_handlers:
                try:
                    handler(msg_data)
                except Exception as e:
                    log.error(f"消息处理器执行失败: {e}")
            
        except Exception as e:
            log.error(f"处理WebSocket消息失败: {e}")
    
    def _on_error(self, ws, error):
        """WebSocket错误回调"""
        log.error(f"WebSocket错误: {error}")
        self.is_connected = False
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket连接关闭回调"""
        log.info(f"WebSocket连接已关闭: {close_status_code}, {close_msg}")
        self.is_connected = False
        
        # 尝试重连
        if self.running and self.reconnect_attempts < self.max_reconnect_attempts:
            self._reconnect()
    
    def _reconnect(self):
        """重连WebSocket"""
        try:
            self.reconnect_attempts += 1
            log.info(f"尝试重连WebSocket ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
            
            time.sleep(self.reconnect_interval)
            
            if self.connect():
                log.info("WebSocket重连成功")
            else:
                log.error("WebSocket重连失败")
                
        except Exception as e:
            log.error(f"WebSocket重连失败: {e}")
    
    def _start_heartbeat(self):
        """启动心跳包"""
        def heartbeat():
            while self.is_connected and self.running:
                try:
                    # 发送心跳包
                    heartbeat_msg = json.dumps({"type": "ping", "timestamp": int(time.time())})
                    self.ws.send(heartbeat_msg)
                    time.sleep(30)  # 每30秒发送一次心跳
                except Exception as e:
                    log.error(f"发送心跳包失败: {e}")
                    break
        
        heartbeat_thread = threading.Thread(target=heartbeat)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
    
    def send_message(self, message_data: Dict) -> bool:
        """发送消息"""
        try:
            if not self.is_connected:
                log.error("WebSocket未连接，无法发送消息")
                return False
            
            message_json = json.dumps(message_data, ensure_ascii=False)
            self.ws.send(message_json)
            log.debug(f"发送WebSocket消息: {message_json}")
            return True
            
        except Exception as e:
            log.error(f"发送WebSocket消息失败: {e}")
            return False
    
    def send_chat_message(self, recipient_id: str, content: str, message_type: str = "text") -> bool:
        """发送聊天消息"""
        try:
            message_data = {
                "type": "chat_message",
                "recipient_id": recipient_id,
                "content": content,
                "message_type": message_type,
                "timestamp": int(time.time() * 1000)
            }
            
            return self.send_message(message_data)
            
        except Exception as e:
            log.error(f"发送聊天消息失败: {e}")
            return False
    
    def add_message_handler(self, handler: Callable):
        """添加消息处理器"""
        self.message_handlers.append(handler)
        log.info("已添加消息处理器")
    
    def remove_message_handler(self, handler: Callable):
        """移除消息处理器"""
        if handler in self.message_handlers:
            self.message_handlers.remove(handler)
            log.info("已移除消息处理器")
    
    def get_recent_messages(self, count: int = 50) -> List[Dict]:
        """获取最近的消息"""
        with self.queue_lock:
            return self.message_queue[-count:] if len(self.message_queue) > count else self.message_queue.copy()
    
    def clear_message_queue(self):
        """清空消息队列"""
        with self.queue_lock:
            self.message_queue.clear()
        log.info("消息队列已清空")
    
    def get_chat_list(self) -> List[Dict]:
        """获取聊天列表"""
        try:
            # 访问聊天列表页面
            self.driver.get("https://i.zhaopin.com/chat")
            time.sleep(2)
            
            chat_list = []
            
            # 解析聊天列表
            chat_items = self.driver.find_elements(By.CLASS_NAME, "chat-item")
            
            for item in chat_items:
                try:
                    chat_info = {
                        'id': item.get_attribute('data-id') or '',
                        'name': '',
                        'avatar': '',
                        'last_message': '',
                        'last_time': '',
                        'unread_count': 0
                    }
                    
                    # 提取聊天信息
                    try:
                        name_element = item.find_element(By.CLASS_NAME, "chat-name")
                        chat_info['name'] = name_element.text.strip()
                    except:
                        pass
                    
                    try:
                        avatar_element = item.find_element(By.CLASS_NAME, "chat-avatar")
                        chat_info['avatar'] = avatar_element.get_attribute('src')
                    except:
                        pass
                    
                    try:
                        last_msg_element = item.find_element(By.CLASS_NAME, "last-message")
                        chat_info['last_message'] = last_msg_element.text.strip()
                    except:
                        pass
                    
                    try:
                        time_element = item.find_element(By.CLASS_NAME, "chat-time")
                        chat_info['last_time'] = time_element.text.strip()
                    except:
                        pass
                    
                    try:
                        unread_element = item.find_element(By.CLASS_NAME, "unread-count")
                        chat_info['unread_count'] = int(unread_element.text.strip())
                    except:
                        pass
                    
                    chat_list.append(chat_info)
                    
                except Exception as e:
                    log.warning(f"解析聊天项失败: {e}")
                    continue
            
            log.info(f"获取到 {len(chat_list)} 个聊天")
            return chat_list
            
        except Exception as e:
            log.error(f"获取聊天列表失败: {e}")
            return []
    
    def enter_chat(self, chat_id: str) -> bool:
        """进入指定聊天"""
        try:
            chat_url = f"https://i.zhaopin.com/chat/{chat_id}"
            self.driver.get(chat_url)
            time.sleep(2)
            
            # 等待聊天界面加载
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "chat-content"))
            )
            
            log.info(f"已进入聊天: {chat_id}")
            return True
            
        except Exception as e:
            log.error(f"进入聊天失败: {e}")
            return False
    
    def get_chat_history(self, chat_id: str, limit: int = 50) -> List[Dict]:
        """获取聊天历史"""
        try:
            if not self.enter_chat(chat_id):
                return []
            
            messages = []
            
            # 获取消息列表
            message_elements = self.driver.find_elements(By.CLASS_NAME, "message-item")
            
            for element in message_elements[-limit:]:
                try:
                    message = {
                        'id': element.get_attribute('data-id') or '',
                        'sender': '',
                        'content': '',
                        'timestamp': '',
                        'type': 'text'
                    }
                    
                    # 提取消息信息
                    try:
                        sender_element = element.find_element(By.CLASS_NAME, "message-sender")
                        message['sender'] = sender_element.text.strip()
                    except:
                        pass
                    
                    try:
                        content_element = element.find_element(By.CLASS_NAME, "message-content")
                        message['content'] = content_element.text.strip()
                    except:
                        pass
                    
                    try:
                        time_element = element.find_element(By.CLASS_NAME, "message-time")
                        message['timestamp'] = time_element.text.strip()
                    except:
                        pass
                    
                    messages.append(message)
                    
                except Exception as e:
                    log.warning(f"解析消息失败: {e}")
                    continue
            
            log.info(f"获取到 {len(messages)} 条聊天历史")
            return messages
            
        except Exception as e:
            log.error(f"获取聊天历史失败: {e}")
            return []
    
    def disconnect(self):
        """断开WebSocket连接"""
        try:
            self.running = False
            self.is_connected = False
            
            if self.ws:
                self.ws.close()
                self.ws = None
            
            log.info("WebSocket连接已断开")
            
        except Exception as e:
            log.error(f"断开WebSocket连接失败: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()