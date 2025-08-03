#!/usr/bin/env python3
"""
测试职位解析功能的脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.login import ZhilianLogin
from modules.candidate import CandidateManager
from utils import log


def test_quick_parsing():
    """快速测试解析功能"""
    print("🧪 测试职位解析功能...")
    
    try:
        # 初始化登录管理器
        login_manager = ZhilianLogin()
        
        # 初始化候选人管理器
        candidate_manager = CandidateManager(login_manager.driver)
        
        print("✅ 浏览器初始化成功")
        
        # 登录
        print("🔐 开始登录...")
        if login_manager.auto_login():
            print("✅ 登录成功")
        else:
            print("❌ 登录失败")
            return
        
        # 测试搜索
        print("🔍 开始搜索Java开发职位...")
        search_params = {
            'keyword': 'Java开发',
            'location': '北京',
            'page_limit': 1  # 只搜索第一页
        }
        
        candidates = candidate_manager.search_candidates(**search_params)
        
        print(f"🎯 搜索完成，找到 {len(candidates)} 个职位")
        
        # 显示前5个职位信息
        for i, candidate in enumerate(candidates[:5], 1):
            print(f"\n📋 职位 {i}:")
            print(f"   职位名称: {candidate.get('name', '未知')}")
            print(f"   公司名称: {candidate.get('company', '未知')}")
            print(f"   薪资范围: {candidate.get('salary', '未知')}")
            print(f"   工作地点: {candidate.get('location', '未知')}")
            print(f"   工作经验: {candidate.get('experience', '未知')}")
            print(f"   学历要求: {candidate.get('education', '未知')}")
            print(f"   职位链接: {candidate.get('profile_url', '无')}")
        
        # 保存结果
        if candidates:
            candidate_manager.save_candidates_to_file(candidates, "test_candidates.json")
            print(f"\n💾 职位信息已保存到 test_candidates.json")
        
        print("\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            login_manager.close()
            print("🔒 浏览器已关闭")
        except:
            pass


def test_url_generation():
    """测试URL生成"""
    print("\n🔗 测试URL生成...")
    
    from modules.candidate import CandidateManager
    
    class MockDriver:
        pass
    
    candidate_manager = CandidateManager(MockDriver())
    
    test_cases = [
        {'keyword': 'Java开发', 'location': '北京'},
        {'keyword': 'Python开发', 'location': '上海'},
        {'keyword': '前端开发', 'location': '深圳'}
    ]
    
    for case in test_cases:
        url = candidate_manager._build_search_url(**case)
        print(f"✅ {case['keyword']} + {case['location']}")
        print(f"   URL: {url}")


if __name__ == "__main__":
    print("🚀 智联招聘解析功能测试")
    print("=" * 50)
    
    # 测试URL生成
    test_url_generation()
    
    # 询问是否进行完整测试
    print("\n" + "=" * 50)
    response = input("是否进行完整的登录和搜索测试？(y/n): ").lower().strip()
    
    if response in ['y', 'yes', '是']:
        test_quick_parsing()
    else:
        print("跳过完整测试")
    
    print("\n✨ 测试结束")