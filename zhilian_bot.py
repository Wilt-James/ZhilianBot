"""
智联招聘自动化工具主程序
"""
import time
import json
import signal
import sys
from typing import Dict, List, Optional

from config import settings
from utils import log
from modules import (
    ZhilianLogin,
    CandidateManager,
    InteractionManager,
    WebSocketChatManager,
    MessageForwarder
)


class ZhilianBot:
    """智联招聘自动化机器人"""
    
    def __init__(self):
        self.login_manager = None
        self.candidate_manager = None
        self.interaction_manager = None
        self.websocket_manager = None
        self.message_forwarder = None
        self.is_running = False
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        log.info("收到退出信号，正在关闭...")
        self.stop()
        sys.exit(0)
    
    def initialize(self) -> bool:
        """初始化机器人"""
        try:
            log.info("正在初始化智联招聘机器人...")
            
            # 初始化登录管理器
            self.login_manager = ZhilianLogin()
            
            # 初始化其他管理器
            self.candidate_manager = CandidateManager(self.login_manager.driver)
            self.interaction_manager = InteractionManager(self.login_manager.driver)
            self.websocket_manager = WebSocketChatManager(self.login_manager.driver)
            
            # 初始化消息转发器
            self.message_forwarder = MessageForwarder()
            
            log.info("机器人初始化完成")
            return True
            
        except Exception as e:
            log.error(f"机器人初始化失败: {e}")
            return False
    
    def login(self) -> bool:
        """登录智联招聘"""
        try:
            if not self.login_manager:
                log.error("登录管理器未初始化")
                return False
            
            return self.login_manager.auto_login()
            
        except Exception as e:
            log.error(f"登录失败: {e}")
            return False
    
    def start_message_forwarding(self) -> bool:
        """启动消息转发服务"""
        try:
            if not self.message_forwarder:
                log.error("消息转发器未初始化")
                return False
            
            # 测试连接
            if not self.message_forwarder.test_connection():
                log.warning("中心服务器连接测试失败，但仍会启动转发服务")
            
            # 启动转发服务
            self.message_forwarder.start()
            
            # 注册机器人
            bot_info = {
                'bot_id': f"zhilian_bot_{int(time.time())}",
                'name': 'Zhilian Recruitment Bot',
                'version': '1.0.0'
            }
            self.message_forwarder.register_bot(bot_info)
            
            return True
            
        except Exception as e:
            log.error(f"启动消息转发服务失败: {e}")
            return False
    
    def start_websocket_chat(self) -> bool:
        """启动WebSocket聊天"""
        try:
            if not self.websocket_manager:
                log.error("WebSocket管理器未初始化")
                return False
            
            # 添加消息处理器
            self.websocket_manager.add_message_handler(self._handle_websocket_message)
            
            # 连接WebSocket
            return self.websocket_manager.connect()
            
        except Exception as e:
            log.error(f"启动WebSocket聊天失败: {e}")
            return False
    
    def _handle_websocket_message(self, message_data: Dict):
        """处理WebSocket消息"""
        try:
            log.debug(f"处理WebSocket消息: {message_data}")
            
            # 转发消息到中心服务器
            if self.message_forwarder:
                self.message_forwarder.forward_message(message_data, "websocket_message")
            
            # 这里可以添加其他消息处理逻辑
            
        except Exception as e:
            log.error(f"处理WebSocket消息失败: {e}")
    
    def search_and_greet_candidates(self, 
                                  search_params: Dict,
                                  greeting_message: str = None,
                                  max_candidates: int = 20) -> Dict:
        """搜索并打招呼候选人"""
        try:
            log.info("开始搜索并打招呼候选人...")
            
            # 搜索候选人
            candidates = self.candidate_manager.search_candidates(
                keyword=search_params.get('keyword', ''),
                location=search_params.get('location', ''),
                experience=search_params.get('experience', ''),
                education=search_params.get('education', ''),
                page_limit=search_params.get('page_limit', 3)
            )
            
            if not candidates:
                log.warning("未找到符合条件的候选人")
                return {'total': 0, 'success': 0, 'failed': 0}
            
            # 限制候选人数量
            candidates = candidates[:max_candidates]
            
            # 批量打招呼
            results = self.interaction_manager.batch_greeting(
                candidates=candidates,
                message_template=greeting_message,
                max_count=max_candidates
            )
            
            # 转发候选人信息和互动事件
            if self.message_forwarder:
                for candidate in candidates:
                    self.message_forwarder.forward_candidate_info(candidate)
                
                self.message_forwarder.forward_interaction_event(
                    event_type="batch_greeting",
                    candidate_id="batch",
                    details=results
                )
            
            return results
            
        except Exception as e:
            log.error(f"搜索并打招呼候选人失败: {e}")
            return {'total': 0, 'success': 0, 'failed': 0}
    
    def get_candidate_details(self, candidate_urls: List[str]) -> List[Dict]:
        """获取候选人详细信息"""
        try:
            log.info(f"获取 {len(candidate_urls)} 个候选人的详细信息...")
            
            detailed_candidates = []
            
            for i, url in enumerate(candidate_urls, 1):
                try:
                    log.info(f"正在获取第 {i}/{len(candidate_urls)} 个职位详情...")
                    
                    # 检查URL有效性
                    if not url or not url.strip():
                        log.warning(f"第 {i} 个URL为空，跳过")
                        continue
                    
                    detail = self.candidate_manager.get_candidate_detail(url)
                    if detail:
                        detailed_candidates.append(detail)
                        
                        # 检查是否获取成功
                        if detail.get('error'):
                            log.warning(f"第 {i} 个职位获取有错误: {detail.get('error')}")
                        else:
                            log.info(f"✓ 第 {i} 个职位获取成功: {detail.get('name', '未知职位')}")
                        
                        # 转发候选人详细信息
                        if self.message_forwarder:
                            self.message_forwarder.forward_candidate_info(detail)
                    else:
                        log.warning(f"第 {i} 个职位详情获取失败，返回为空")
                    
                    # 避免请求过快
                    time.sleep(settings.REQUEST_DELAY * 2)  # 增加延迟
                    
                except Exception as e:
                    log.error(f"获取第 {i} 个候选人详细信息失败 {url}: {e}")
                    # 添加错误信息到结果中
                    error_detail = {
                        'url': url,
                        'error': str(e),
                        'name': '获取失败',
                        'status': 'error'
                    }
                    detailed_candidates.append(error_detail)
                    continue
            
            success_count = len([d for d in detailed_candidates if not d.get('error')])
            error_count = len([d for d in detailed_candidates if d.get('error')])
            
            log.info(f"候选人详情获取完成: 成功 {success_count} 个，失败 {error_count} 个，总计 {len(detailed_candidates)} 个")
            return detailed_candidates
            
        except Exception as e:
            log.error(f"获取候选人详细信息失败: {e}")
            return []
    
    def monitor_chats(self):
        """监控聊天消息"""
        try:
            log.info("开始监控聊天消息...")
            
            while self.is_running:
                try:
                    # 获取聊天列表
                    chat_list = self.websocket_manager.get_chat_list()
                    
                    for chat in chat_list:
                        if chat.get('unread_count', 0) > 0:
                            log.info(f"发现新消息: {chat['name']} ({chat['unread_count']} 条)")
                            
                            # 获取聊天历史
                            messages = self.websocket_manager.get_chat_history(
                                chat['id'], 
                                limit=chat['unread_count']
                            )
                            
                            # 转发新消息
                            if self.message_forwarder:
                                for message in messages:
                                    self.message_forwarder.forward_chat_message(
                                        sender_id=message.get('sender', ''),
                                        recipient_id='bot',
                                        content=message.get('content', ''),
                                        message_id=message.get('id', ''),
                                        chat_id=chat['id']
                                    )
                    
                    # 检查待执行命令
                    if self.message_forwarder:
                        commands = self.message_forwarder.get_pending_commands()
                        for command in commands:
                            self._execute_command(command)
                    
                    time.sleep(5)  # 每5秒检查一次
                    
                except Exception as e:
                    log.error(f"监控聊天消息时出错: {e}")
                    time.sleep(10)
            
        except Exception as e:
            log.error(f"监控聊天消息失败: {e}")
    
    def _execute_command(self, command: Dict):
        """执行远程命令"""
        try:
            command_type = command.get('type', '')
            command_id = command.get('id', '')
            params = command.get('params', {})
            
            log.info(f"执行命令: {command_type} ({command_id})")
            
            result = {'success': False, 'message': '未知命令类型'}
            
            if command_type == 'search_candidates':
                # 搜索候选人
                candidates = self.candidate_manager.search_candidates(**params)
                result = {'success': True, 'data': candidates, 'count': len(candidates)}
                
            elif command_type == 'send_greeting':
                # 发送打招呼
                success = self.interaction_manager.send_greeting(**params)
                result = {'success': success, 'message': '打招呼发送成功' if success else '打招呼发送失败'}
                
            elif command_type == 'get_chat_list':
                # 获取聊天列表
                chats = self.websocket_manager.get_chat_list()
                result = {'success': True, 'data': chats, 'count': len(chats)}
                
            elif command_type == 'send_message':
                # 发送消息
                success = self.websocket_manager.send_chat_message(**params)
                result = {'success': success, 'message': '消息发送成功' if success else '消息发送失败'}
            
            # 确认命令执行结果
            if self.message_forwarder:
                self.message_forwarder.acknowledge_command(command_id, result)
            
        except Exception as e:
            log.error(f"执行命令失败: {e}")
            
            # 确认命令执行失败
            if self.message_forwarder:
                result = {'success': False, 'message': str(e)}
                self.message_forwarder.acknowledge_command(command.get('id', ''), result)
    
    def run(self):
        """运行机器人"""
        try:
            log.info("启动智联招聘机器人...")
            
            # 初始化
            if not self.initialize():
                log.error("机器人初始化失败")
                return False
            
            # 登录
            if not self.login():
                log.error("登录失败")
                return False
            
            # 启动消息转发服务
            self.start_message_forwarding()
            
            # 启动WebSocket聊天
            self.start_websocket_chat()
            
            # 设置运行状态
            self.is_running = True
            
            log.info("机器人启动成功，开始监控...")
            
            # 开始监控聊天
            self.monitor_chats()
            
        except Exception as e:
            log.error(f"运行机器人失败: {e}")
            return False
        finally:
            self.stop()
    
    def stop(self):
        """停止机器人"""
        try:
            log.info("正在停止机器人...")
            
            self.is_running = False
            
            # 停止WebSocket连接
            if self.websocket_manager:
                self.websocket_manager.disconnect()
            
            # 停止消息转发服务
            if self.message_forwarder:
                self.message_forwarder.stop()
            
            # 关闭浏览器
            if self.login_manager:
                self.login_manager.close()
            
            log.info("机器人已停止")
            
        except Exception as e:
            log.error(f"停止机器人失败: {e}")
    
    def get_status(self) -> Dict:
        """获取机器人状态"""
        status = {
            'is_running': self.is_running,
            'login_status': False,
            'websocket_status': False,
            'forwarder_status': {}
        }
        
        try:
            if self.login_manager:
                status['login_status'] = self.login_manager.is_logged_in()
            
            if self.websocket_manager:
                status['websocket_status'] = self.websocket_manager.is_connected
            
            if self.message_forwarder:
                status['forwarder_status'] = self.message_forwarder.get_status()
        
        except Exception as e:
            log.error(f"获取状态失败: {e}")
        
        return status


def main():
    """主函数"""
    try:
        bot = ZhilianBot()
        bot.run()
    except KeyboardInterrupt:
        log.info("用户中断程序")
    except Exception as e:
        log.error(f"程序异常退出: {e}")


if __name__ == "__main__":
    main()