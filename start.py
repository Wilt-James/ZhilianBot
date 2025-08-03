#!/usr/bin/env python3
"""
智联招聘机器人启动脚本
"""
import argparse
import sys
import os

from zhilian_bot import ZhilianBot
from utils import log


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智联招聘自动化工具")
    parser.add_argument("--mode", choices=["full", "search", "monitor", "test"], 
                       default="full", help="运行模式")
    parser.add_argument("--headless", action="store_true", help="无头模式运行")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--keyword", help="搜索关键词")
    parser.add_argument("--location", help="工作地点")
    parser.add_argument("--max-candidates", type=int, default=20, help="最大候选人数量")
    
    args = parser.parse_args()
    
    # 设置无头模式
    if args.headless:
        os.environ['HEADLESS'] = 'true'
    
    # 设置配置文件
    if args.config:
        os.environ['CONFIG_FILE'] = args.config
    
    try:
        if args.mode == "full":
            # 完整模式：运行所有功能
            log.info("启动完整模式...")
            bot = ZhilianBot()
            bot.run()
            
        elif args.mode == "search":
            # 搜索模式：只搜索候选人
            log.info("启动搜索模式...")
            bot = ZhilianBot()
            
            if not bot.initialize() or not bot.login():
                log.error("初始化或登录失败")
                return 1
            
            search_params = {
                'keyword': args.keyword or 'Python开发',
                'location': args.location or '北京',
                'page_limit': 3
            }
            
            candidates = bot.candidate_manager.search_candidates(**search_params)
            log.info(f"找到 {len(candidates)} 个候选人")
            
            # 保存结果
            bot.candidate_manager.save_candidates_to_file(candidates)
            bot.stop()
            
        elif args.mode == "monitor":
            # 监控模式：只监控聊天
            log.info("启动监控模式...")
            bot = ZhilianBot()
            
            if not bot.initialize() or not bot.login():
                log.error("初始化或登录失败")
                return 1
            
            bot.start_message_forwarding()
            bot.start_websocket_chat()
            bot.is_running = True
            
            log.info("开始监控聊天消息，按Ctrl+C停止...")
            bot.monitor_chats()
            
        elif args.mode == "test":
            # 测试模式：测试各个功能
            log.info("启动测试模式...")
            bot = ZhilianBot()
            
            if not bot.initialize():
                log.error("初始化失败")
                return 1
            
            # 测试登录
            if bot.login():
                log.info("✓ 登录测试通过")
            else:
                log.error("✗ 登录测试失败")
                return 1
            
            # 测试搜索
            try:
                candidates = bot.candidate_manager.search_candidates(
                    keyword="测试", page_limit=1
                )
                log.info(f"✓ 搜索测试通过，找到 {len(candidates)} 个候选人")
            except Exception as e:
                log.error(f"✗ 搜索测试失败: {e}")
            
            # 测试WebSocket
            try:
                if bot.start_websocket_chat():
                    log.info("✓ WebSocket测试通过")
                else:
                    log.warning("✗ WebSocket测试失败")
            except Exception as e:
                log.error(f"✗ WebSocket测试失败: {e}")
            
            # 测试消息转发
            try:
                bot.start_message_forwarding()
                if bot.message_forwarder.test_connection():
                    log.info("✓ 消息转发测试通过")
                else:
                    log.warning("✗ 消息转发测试失败（可能是服务器未配置）")
            except Exception as e:
                log.error(f"✗ 消息转发测试失败: {e}")
            
            bot.stop()
            log.info("测试完成")
        
        return 0
        
    except KeyboardInterrupt:
        log.info("用户中断程序")
        return 0
    except Exception as e:
        log.error(f"程序异常: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())