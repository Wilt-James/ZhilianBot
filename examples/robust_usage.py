"""
稳定版基本使用示例 - 使用test_robust_login.py中的稳定登录逻辑
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zhilian_bot import ZhilianBot
from utils import log


def example_robust_search_and_greet():
    """示例：使用稳定登录进行搜索候选人并打招呼"""
    bot = ZhilianBot()
    
    try:
        # 初始化和登录
        if not bot.initialize():
            log.error("初始化失败")
            return
        
        log.info("🛡️ 使用稳定登录逻辑...")
        if not bot.login():
            log.error("登录失败")
            return
        
        # 搜索参数
        search_params = {
            'keyword': 'Python开发工程师',
            'location': '北京',
            'experience': '3-5年',
            'education': '本科',
            'page_limit': 2
        }
        
        # 自定义打招呼消息
        greeting_message = """您好！我是某某科技的HR，看到您在Python开发方面的经验很丰富，我们公司目前有一个很不错的Python后端开发职位，薪资15-25K，工作地点在北京朝阳区。如果您有兴趣了解详情，欢迎和我聊聊！"""
        
        # 搜索并打招呼
        results = bot.search_and_greet_candidates(
            search_params=search_params,
            greeting_message=greeting_message,
            max_candidates=10
        )
        
        log.info(f"搜索并打招呼完成: {results}")
        
    except Exception as e:
        log.error(f"示例执行失败: {e}")
    finally:
        bot.stop()


def example_robust_monitor_chats():
    """示例：使用稳定登录进行监控聊天消息"""
    bot = ZhilianBot()
    
    try:
        # 初始化和登录
        if not bot.initialize():
            log.error("初始化失败")
            return
        
        log.info("🛡️ 使用稳定登录逻辑...")
        if not bot.login():
            log.error("登录失败")
            return
        
        # 启动消息转发服务
        bot.start_message_forwarding()
        
        # 启动WebSocket聊天
        bot.start_websocket_chat()
        
        # 设置运行状态
        bot.is_running = True
        
        log.info("开始监控聊天消息，按Ctrl+C停止...")
        
        # 监控聊天
        bot.monitor_chats()
        
    except KeyboardInterrupt:
        log.info("用户停止监控")
    except Exception as e:
        log.error(f"监控失败: {e}")
    finally:
        bot.stop()


def example_robust_get_candidate_details():
    """示例：使用稳定登录获取候选人详细信息"""
    bot = ZhilianBot()
    
    try:
        # 初始化和登录
        if not bot.initialize():
            log.error("初始化失败")
            return
        
        log.info("🛡️ 使用稳定登录逻辑...")
        if not bot.login():
            log.error("登录失败")
            return
        
        # 先搜索候选人
        search_params = {
            'keyword': 'Java开发',
            'location': '上海',
            'page_limit': 1
        }
        
        candidates = bot.candidate_manager.search_candidates(**search_params)
        
        if candidates:
            log.info(f"搜索到 {len(candidates)} 个职位")
            
            # 显示搜索结果
            for i, candidate in enumerate(candidates[:10], 1):
                log.info(f"职位 {i}: {candidate.get('name', '未知')} - {candidate.get('company', '未知')} - {candidate.get('salary', '未知')}")
            
            # 获取前3个候选人的详细信息（减少数量避免问题）
            candidate_urls = []
            for candidate in candidates[:3]:
                url = candidate.get('profile_url', '')
                if url and url.strip():
                    candidate_urls.append(url)
            
            log.info(f"准备获取 {len(candidate_urls)} 个职位的详细信息...")
            
            if candidate_urls:
                detailed_info = bot.get_candidate_details(candidate_urls)
                
                # 保存到文件
                if detailed_info:
                    bot.candidate_manager.save_candidates_to_file(detailed_info, "robust_detailed_candidates.json")
                    log.info(f"获取了 {len(detailed_info)} 个候选人的详细信息")
                    
                    # 显示详细信息摘要
                    for i, detail in enumerate(detailed_info, 1):
                        log.info(f"详情 {i}: {detail.get('name', '未知')} - 状态: {detail.get('status', '成功')}")
                else:
                    log.warning("未能获取任何详细信息")
            else:
                log.warning("没有有效的职位详情URL")
        else:
            log.warning("未找到候选人")
        
    except Exception as e:
        log.error(f"示例执行失败: {e}")
    finally:
        bot.stop()


def example_robust_simple_search():
    """示例：简单的稳定搜索测试"""
    bot = ZhilianBot()
    
    try:
        # 初始化和登录
        if not bot.initialize():
            log.error("初始化失败")
            return
        
        log.info("🛡️ 使用稳定登录逻辑...")
        if not bot.login():
            log.error("登录失败")
            return
        
        log.info("🔍 开始搜索测试...")
        
        # 搜索参数
        search_params = {
            'keyword': 'Java开发',
            'location': '北京',
            'page_limit': 1
        }
        
        candidates = bot.candidate_manager.search_candidates(**search_params)
        log.info(f"🎯 搜索完成，找到 {len(candidates)} 个职位")
        
        # 显示结果
        for i, candidate in enumerate(candidates[:5], 1):
            log.info(f"📋 职位 {i}: {candidate.get('name', '未知')} - {candidate.get('company', '未知')}")
        
        if candidates:
            bot.candidate_manager.save_candidates_to_file(candidates, "robust_search_results.json")
            log.info("💾 结果已保存到 robust_search_results.json")
        
        log.info("🎉 测试完成！")
        
    except Exception as e:
        log.error(f"示例执行失败: {e}")
    finally:
        bot.stop()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="智联招聘机器人稳定版示例")
    parser.add_argument("--example", choices=["search", "monitor", "details", "simple"], 
                       default="simple", help="选择要运行的示例")
    
    args = parser.parse_args()
    
    print("🛡️ 智联招聘机器人稳定版示例")
    print("=" * 50)
    print("使用test_robust_login.py中的稳定登录逻辑")
    print("=" * 50)
    
    if args.example == "search":
        example_robust_search_and_greet()
    elif args.example == "monitor":
        example_robust_monitor_chats()
    elif args.example == "details":
        example_robust_get_candidate_details()
    elif args.example == "simple":
        example_robust_simple_search()
    else:
        log.error("未知的示例类型")