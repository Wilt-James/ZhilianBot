"""
高级使用示例
"""
import sys
import os
import time
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zhilian_bot import ZhilianBot
from modules import MessageForwarder
from utils import log


def example_custom_message_handler():
    """示例：自定义消息处理器"""
    
    def custom_handler(message_data):
        """自定义消息处理函数"""
        try:
            msg_type = message_data.get('type', '')
            
            if msg_type == 'chat_message':
                sender = message_data.get('sender', '未知')
                content = message_data.get('content', '')
                log.info(f"收到来自 {sender} 的消息: {content}")
                
                # 自动回复逻辑
                if '简历' in content or '职位' in content:
                    # 这里可以添加自动回复逻辑
                    log.info("检测到关键词，可以自动回复")
            
            elif msg_type == 'system_notification':
                log.info(f"系统通知: {message_data}")
            
        except Exception as e:
            log.error(f"自定义消息处理失败: {e}")
    
    bot = ZhilianBot()
    
    try:
        if not bot.initialize() or not bot.login():
            return
        
        # 添加自定义消息处理器
        bot.websocket_manager.add_message_handler(custom_handler)
        
        # 启动WebSocket
        bot.start_websocket_chat()
        
        log.info("自定义消息处理器已启动，监控中...")
        
        # 保持运行
        bot.is_running = True
        while bot.is_running:
            time.sleep(1)
    
    except KeyboardInterrupt:
        log.info("用户停止程序")
    finally:
        bot.stop()


def example_batch_operations():
    """示例：批量操作"""
    bot = ZhilianBot()
    
    try:
        if not bot.initialize() or not bot.login():
            return
        
        # 定义多个搜索任务
        search_tasks = [
            {
                'keyword': 'Python开发',
                'location': '北京',
                'experience': '3-5年',
                'page_limit': 2
            },
            {
                'keyword': 'Java开发',
                'location': '上海',
                'experience': '5-10年',
                'page_limit': 2
            },
            {
                'keyword': '前端开发',
                'location': '深圳',
                'experience': '1-3年',
                'page_limit': 1
            }
        ]
        
        all_candidates = []
        
        # 批量搜索
        for i, task in enumerate(search_tasks):
            log.info(f"执行搜索任务 {i+1}/{len(search_tasks)}: {task['keyword']}")
            
            candidates = bot.candidate_manager.search_candidates(**task)
            all_candidates.extend(candidates)
            
            log.info(f"任务 {i+1} 找到 {len(candidates)} 个候选人")
            
            # 避免请求过快
            time.sleep(2)
        
        log.info(f"批量搜索完成，总共找到 {len(all_candidates)} 个候选人")
        
        # 保存结果
        bot.candidate_manager.save_candidates_to_file(all_candidates, "batch_candidates.json")
        
        # 批量打招呼（限制数量）
        if all_candidates:
            greeting_results = bot.interaction_manager.batch_greeting(
                candidates=all_candidates[:20],  # 限制20个
                message_template="您好，我们公司有适合您的职位机会，想和您聊聊。",
                max_count=20
            )
            
            log.info(f"批量打招呼结果: {greeting_results}")
    
    except Exception as e:
        log.error(f"批量操作失败: {e}")
    finally:
        bot.stop()


def example_message_forwarding():
    """示例：消息转发功能"""
    
    # 独立测试消息转发器
    forwarder = MessageForwarder()
    
    try:
        # 测试连接
        if forwarder.test_connection():
            log.info("中心服务器连接正常")
        else:
            log.warning("中心服务器连接失败，但继续演示")
        
        # 启动转发服务
        forwarder.start()
        
        # 模拟转发各种类型的消息
        
        # 1. 转发候选人信息
        candidate_data = {
            'id': 'candidate_001',
            'name': '张三',
            'position': 'Python开发工程师',
            'company': '某某科技',
            'experience': '3年',
            'education': '本科',
            'skills': ['Python', 'Django', 'MySQL']
        }
        forwarder.forward_candidate_info(candidate_data)
        
        # 2. 转发聊天消息
        forwarder.forward_chat_message(
            sender_id='candidate_001',
            recipient_id='hr_001',
            content='您好，我对这个职位很感兴趣',
            chat_id='chat_001'
        )
        
        # 3. 转发互动事件
        forwarder.forward_interaction_event(
            event_type='greeting_sent',
            candidate_id='candidate_001',
            details={'message': '打招呼消息已发送', 'timestamp': int(time.time())}
        )
        
        # 4. 发送心跳包
        forwarder.send_heartbeat()
        
        log.info("消息转发示例完成")
        
        # 等待消息发送完成
        time.sleep(5)
        
        # 查看队列状态
        status = forwarder.get_status()
        log.info(f"转发器状态: {status}")
    
    except Exception as e:
        log.error(f"消息转发示例失败: {e}")
    finally:
        forwarder.stop()


def example_full_workflow():
    """示例：完整工作流程"""
    bot = ZhilianBot()
    
    try:
        log.info("开始完整工作流程演示...")
        
        # 1. 初始化和登录
        if not bot.initialize():
            log.error("初始化失败")
            return
        
        if not bot.login():
            log.error("登录失败")
            return
        
        # 2. 启动所有服务
        bot.start_message_forwarding()
        bot.start_websocket_chat()
        
        # 3. 搜索候选人
        search_params = {
            'keyword': 'Python开发工程师',
            'location': '北京',
            'experience': '3-5年',
            'page_limit': 2
        }
        
        candidates = bot.candidate_manager.search_candidates(**search_params)
        log.info(f"找到 {len(candidates)} 个候选人")
        
        if not candidates:
            log.warning("未找到候选人，结束流程")
            return
        
        # 4. 获取详细信息
        candidate_urls = [c.get('profile_url') for c in candidates[:5] if c.get('profile_url')]
        detailed_candidates = bot.get_candidate_details(candidate_urls)
        
        # 5. 批量打招呼
        greeting_results = bot.interaction_manager.batch_greeting(
            candidates=candidates[:10],
            message_template="您好，我们公司有很好的Python开发职位，想和您聊聊。",
            max_count=10
        )
        
        log.info(f"打招呼结果: {greeting_results}")
        
        # 6. 监控聊天（短时间）
        bot.is_running = True
        log.info("开始监控聊天消息（30秒）...")
        
        start_time = time.time()
        while time.time() - start_time < 30 and bot.is_running:
            try:
                # 检查新消息
                chat_list = bot.websocket_manager.get_chat_list()
                
                for chat in chat_list:
                    if chat.get('unread_count', 0) > 0:
                        log.info(f"发现新消息: {chat['name']}")
                
                time.sleep(5)
                
            except Exception as e:
                log.error(f"监控过程中出错: {e}")
                break
        
        log.info("完整工作流程演示完成")
    
    except Exception as e:
        log.error(f"完整工作流程失败: {e}")
    finally:
        bot.stop()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="智联招聘机器人高级示例")
    parser.add_argument("--example", 
                       choices=["handler", "batch", "forwarding", "workflow"], 
                       default="workflow", 
                       help="选择要运行的高级示例")
    
    args = parser.parse_args()
    
    if args.example == "handler":
        example_custom_message_handler()
    elif args.example == "batch":
        example_batch_operations()
    elif args.example == "forwarding":
        example_message_forwarding()
    elif args.example == "workflow":
        example_full_workflow()
    else:
        log.error("未知的示例类型")