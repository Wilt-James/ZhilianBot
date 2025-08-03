"""
消息转发模块 - 将智联招聘的消息转发到中心服务器
"""
import json
import time
import asyncio
import threading
from typing import Dict, List, Optional, Callable
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import aiohttp

from config import settings
from utils import log


class MessageForwarder:
    """消息转发器"""
    
    def __init__(self):
        self.center_server_url = settings.CENTER_SERVER_URL
        self.auth_token = settings.CENTER_SERVER_TOKEN
        self.session = None
        self.async_session = None
        self.is_running = False
        self.message_queue = []
        self.queue_lock = threading.Lock()
        self.worker_thread = None
        
        # 重试配置
        self.max_retries = settings.MAX_RETRY_ATTEMPTS
        self.retry_delay = 1.0
        
        self._setup_session()
    
    def _setup_session(self):
        """设置HTTP会话"""
        try:
            self.session = requests.Session()
            
            # 设置重试策略
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
            
            # 设置默认headers
            self.session.headers.update({
                'Content-Type': 'application/json',
                'User-Agent': 'ZhilianBot/1.0',
                'Authorization': f'Bearer {self.auth_token}' if self.auth_token else ''
            })
            
            log.info("HTTP会话初始化成功")
            
        except Exception as e:
            log.error(f"HTTP会话初始化失败: {e}")
    
    def start(self):
        """启动消息转发服务"""
        try:
            if self.is_running:
                log.warning("消息转发服务已在运行")
                return
            
            if not self.center_server_url:
                log.error("中心服务器URL未配置，无法启动消息转发服务")
                return
            
            self.is_running = True
            
            # 启动工作线程
            self.worker_thread = threading.Thread(target=self._worker_loop)
            self.worker_thread.daemon = True
            self.worker_thread.start()
            
            log.info("消息转发服务已启动")
            
        except Exception as e:
            log.error(f"启动消息转发服务失败: {e}")
    
    def stop(self):
        """停止消息转发服务"""
        try:
            self.is_running = False
            
            if self.worker_thread and self.worker_thread.is_alive():
                self.worker_thread.join(timeout=5)
            
            if self.session:
                self.session.close()
            
            log.info("消息转发服务已停止")
            
        except Exception as e:
            log.error(f"停止消息转发服务失败: {e}")
    
    def _worker_loop(self):
        """工作线程循环"""
        while self.is_running:
            try:
                # 处理消息队列
                messages_to_send = []
                
                with self.queue_lock:
                    if self.message_queue:
                        # 批量处理消息，每次最多处理10条
                        batch_size = min(10, len(self.message_queue))
                        messages_to_send = self.message_queue[:batch_size]
                        self.message_queue = self.message_queue[batch_size:]
                
                if messages_to_send:
                    self._send_batch_messages(messages_to_send)
                
                # 短暂休眠
                time.sleep(0.5)
                
            except Exception as e:
                log.error(f"消息转发工作线程错误: {e}")
                time.sleep(1)
    
    def forward_message(self, message_data: Dict, message_type: str = "chat") -> bool:
        """转发单条消息"""
        try:
            # 构建转发消息格式
            forward_data = {
                'source': 'zhilian',
                'type': message_type,
                'timestamp': int(time.time() * 1000),
                'data': message_data
            }
            
            # 添加到队列
            with self.queue_lock:
                self.message_queue.append(forward_data)
            
            log.debug(f"消息已添加到转发队列: {message_type}")
            return True
            
        except Exception as e:
            log.error(f"转发消息失败: {e}")
            return False
    
    def forward_chat_message(self, 
                           sender_id: str,
                           recipient_id: str,
                           content: str,
                           message_id: str = None,
                           chat_id: str = None) -> bool:
        """转发聊天消息"""
        try:
            message_data = {
                'message_id': message_id or f"zhilian_{int(time.time() * 1000)}",
                'chat_id': chat_id,
                'sender_id': sender_id,
                'recipient_id': recipient_id,
                'content': content,
                'platform': 'zhilian',
                'timestamp': int(time.time() * 1000)
            }
            
            return self.forward_message(message_data, "chat_message")
            
        except Exception as e:
            log.error(f"转发聊天消息失败: {e}")
            return False
    
    def forward_candidate_info(self, candidate_data: Dict) -> bool:
        """转发候选人信息"""
        try:
            return self.forward_message(candidate_data, "candidate_info")
        except Exception as e:
            log.error(f"转发候选人信息失败: {e}")
            return False
    
    def forward_interaction_event(self, 
                                event_type: str,
                                candidate_id: str,
                                details: Dict = None) -> bool:
        """转发互动事件（如打招呼、查看简历等）"""
        try:
            event_data = {
                'event_type': event_type,
                'candidate_id': candidate_id,
                'platform': 'zhilian',
                'timestamp': int(time.time() * 1000),
                'details': details or {}
            }
            
            return self.forward_message(event_data, "interaction_event")
            
        except Exception as e:
            log.error(f"转发互动事件失败: {e}")
            return False
    
    def _send_batch_messages(self, messages: List[Dict]) -> bool:
        """批量发送消息"""
        try:
            if not messages:
                return True
            
            # 构建批量请求数据
            batch_data = {
                'messages': messages,
                'batch_id': f"batch_{int(time.time() * 1000)}",
                'source': 'zhilian_bot',
                'timestamp': int(time.time() * 1000)
            }
            
            # 发送到中心服务器
            response = self.session.post(
                f"{self.center_server_url}/messages/batch",
                json=batch_data,
                timeout=30
            )
            
            if response.status_code == 200:
                log.info(f"成功转发 {len(messages)} 条消息")
                return True
            else:
                log.error(f"转发消息失败，状态码: {response.status_code}, 响应: {response.text}")
                
                # 如果是客户端错误，不重试
                if 400 <= response.status_code < 500:
                    return False
                
                # 服务器错误，重新加入队列
                with self.queue_lock:
                    self.message_queue.extend(messages)
                return False
                
        except requests.exceptions.RequestException as e:
            log.error(f"发送消息网络错误: {e}")
            
            # 网络错误，重新加入队列
            with self.queue_lock:
                self.message_queue.extend(messages)
            return False
            
        except Exception as e:
            log.error(f"发送批量消息失败: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """发送心跳包"""
        try:
            heartbeat_data = {
                'type': 'heartbeat',
                'source': 'zhilian_bot',
                'timestamp': int(time.time() * 1000),
                'status': 'online'
            }
            
            response = self.session.post(
                f"{self.center_server_url}/heartbeat",
                json=heartbeat_data,
                timeout=10
            )
            
            if response.status_code == 200:
                log.debug("心跳包发送成功")
                return True
            else:
                log.warning(f"心跳包发送失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            log.error(f"发送心跳包失败: {e}")
            return False
    
    def register_bot(self, bot_info: Dict) -> bool:
        """注册机器人到中心服务器"""
        try:
            register_data = {
                'bot_type': 'zhilian',
                'bot_id': bot_info.get('bot_id', f"zhilian_bot_{int(time.time())}"),
                'name': bot_info.get('name', 'Zhilian Bot'),
                'version': bot_info.get('version', '1.0.0'),
                'capabilities': [
                    'candidate_search',
                    'message_sending',
                    'real_time_chat',
                    'profile_extraction'
                ],
                'status': 'online',
                'timestamp': int(time.time() * 1000)
            }
            
            response = self.session.post(
                f"{self.center_server_url}/bots/register",
                json=register_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                log.info(f"机器人注册成功: {result}")
                return True
            else:
                log.error(f"机器人注册失败，状态码: {response.status_code}, 响应: {response.text}")
                return False
                
        except Exception as e:
            log.error(f"注册机器人失败: {e}")
            return False
    
    def get_pending_commands(self) -> List[Dict]:
        """获取待执行的命令"""
        try:
            response = self.session.get(
                f"{self.center_server_url}/commands/pending",
                timeout=10
            )
            
            if response.status_code == 200:
                commands = response.json().get('commands', [])
                log.debug(f"获取到 {len(commands)} 个待执行命令")
                return commands
            else:
                log.warning(f"获取待执行命令失败，状态码: {response.status_code}")
                return []
                
        except Exception as e:
            log.error(f"获取待执行命令失败: {e}")
            return []
    
    def acknowledge_command(self, command_id: str, result: Dict) -> bool:
        """确认命令执行结果"""
        try:
            ack_data = {
                'command_id': command_id,
                'result': result,
                'timestamp': int(time.time() * 1000)
            }
            
            response = self.session.post(
                f"{self.center_server_url}/commands/{command_id}/ack",
                json=ack_data,
                timeout=10
            )
            
            if response.status_code == 200:
                log.debug(f"命令确认成功: {command_id}")
                return True
            else:
                log.warning(f"命令确认失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            log.error(f"确认命令失败: {e}")
            return False
    
    def get_queue_size(self) -> int:
        """获取消息队列大小"""
        with self.queue_lock:
            return len(self.message_queue)
    
    def clear_queue(self):
        """清空消息队列"""
        with self.queue_lock:
            self.message_queue.clear()
        log.info("消息队列已清空")
    
    def get_status(self) -> Dict:
        """获取转发器状态"""
        return {
            'is_running': self.is_running,
            'queue_size': self.get_queue_size(),
            'center_server_url': self.center_server_url,
            'has_auth_token': bool(self.auth_token),
            'worker_thread_alive': self.worker_thread.is_alive() if self.worker_thread else False
        }
    
    def test_connection(self) -> bool:
        """测试与中心服务器的连接"""
        try:
            if not self.center_server_url:
                log.error("中心服务器URL未配置")
                return False
            
            response = self.session.get(
                f"{self.center_server_url}/health",
                timeout=10
            )
            
            if response.status_code == 200:
                log.info("中心服务器连接测试成功")
                return True
            else:
                log.error(f"中心服务器连接测试失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            log.error(f"中心服务器连接测试失败: {e}")
            return False
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()