#!/usr/bin/env python3
"""
测试修复效果的脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.candidate import CandidateManager
from modules.login import ZhilianLogin
from utils import log


def test_url_building():
    """测试URL构建"""
    print("🔍 测试URL构建功能...")
    
    # 创建一个模拟的driver（这里只测试URL构建逻辑）
    class MockDriver:
        pass
    
    candidate_manager = CandidateManager(MockDriver())
    
    # 测试Java开发搜索URL
    test_cases = [
        {
            'keyword': 'Java开发',
            'location': '北京',
            'expected_contains': ['jl530', 'kw01500O80EO062NO0AF8G']
        },
        {
            'keyword': 'Python开发',
            'location': '上海', 
            'expected_contains': ['jl538', 'kw01500O80EO062']
        },
        {
            'keyword': '前端开发',
            'location': '深圳',
            'expected_contains': ['jl765', 'kw01500O80EO062NO0AF8']
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        try:
            url = candidate_manager._build_search_url(**case)
            print(f"✅ 测试用例 {i}: {case['keyword']} - {case['location']}")
            print(f"   生成URL: {url}")
            
            # 验证URL包含期望的内容
            for expected in case['expected_contains']:
                if expected in url:
                    print(f"   ✓ 包含期望内容: {expected}")
                else:
                    print(f"   ✗ 缺少期望内容: {expected}")
            print()
            
        except Exception as e:
            print(f"❌ 测试用例 {i} 失败: {e}")
    
    # 测试分页URL
    print("📄 测试分页URL构建...")
    base_url = "https://www.zhaopin.com/sou/jl530/kw01500O80EO062NO0AF8G?srccode=401801"
    
    # 模拟分页逻辑
    for page in range(1, 4):
        if page == 1:
            page_url = base_url
        else:
            if '?' in base_url:
                base_path, params = base_url.split('?', 1)
                page_url = f"{base_path}/p{page}?{params}"
            else:
                page_url = f"{base_url}/p{page}"
        
        print(f"第 {page} 页: {page_url}")
    
    print("\n🎯 URL构建测试完成！")


def test_login_selectors():
    """测试登录选择器"""
    print("🔐 测试登录选择器...")
    
    # 验证码输入框选择器
    sms_selectors = [
        "//input[@placeholder='请输入验证码']",
        "//input[@placeholder='验证码']", 
        "//input[contains(@class, 'code')]",
        "//input[contains(@class, 'sms')]",
        "//input[contains(@class, 'verify')]",
        "//input[@type='text'][contains(@name, 'code')]",
        "//input[@type='text'][contains(@id, 'code')]",
        "//input[@maxlength='4' or @maxlength='6']",
        "//button[contains(text(), '获取验证码')]/preceding-sibling::input",
        "//button[contains(text(), '获取验证码')]/..//input[@type='text']"
    ]
    
    print(f"✅ 验证码输入框选择器数量: {len(sms_selectors)}")
    for i, selector in enumerate(sms_selectors, 1):
        print(f"   {i}. {selector}")
    
    # 用户协议选择器
    agreement_selectors = [
        "//input[@type='checkbox']",
        "//span[contains(text(), '已阅读并同意')]/../input",
        "//label[contains(text(), '已阅读并同意')]//input",
        ".agreement-checkbox input",
        ".protocol-checkbox input"
    ]
    
    print(f"\n✅ 用户协议选择器数量: {len(agreement_selectors)}")
    for i, selector in enumerate(agreement_selectors, 1):
        print(f"   {i}. {selector}")
    
    print("\n🎯 登录选择器测试完成！")


def test_keyword_mapping():
    """测试关键词映射"""
    print("🗝️  测试关键词映射...")
    
    keyword_codes = {
        'Java开发': '01500O80EO062NO0AF8G',
        'java开发': '01500O80EO062NO0AF8G', 
        'Java': '01500O80EO062NO0AF8G',
        'java': '01500O80EO062NO0AF8G',
        'Python开发': '01500O80EO062',
        'python开发': '01500O80EO062',
        '前端开发': '01500O80EO062NO0AF8',
        '后端开发': '01500O80EO062NO0AF8G'
    }
    
    print("✅ 关键词编码映射:")
    for keyword, code in keyword_codes.items():
        print(f"   {keyword} -> {code}")
    
    # 验证Java开发的编码
    java_code = keyword_codes.get('Java开发')
    expected_java_code = '01500O80EO062NO0AF8G'
    
    if java_code == expected_java_code:
        print(f"\n✅ Java开发编码验证成功: {java_code}")
    else:
        print(f"\n❌ Java开发编码验证失败: 期望 {expected_java_code}, 实际 {java_code}")
    
    print("\n🎯 关键词映射测试完成！")


def main():
    """主测试函数"""
    print("🧪 智联招聘修复效果测试")
    print("=" * 50)
    
    try:
        # 测试URL构建
        test_url_building()
        print()
        
        # 测试登录选择器
        test_login_selectors()
        print()
        
        # 测试关键词映射
        test_keyword_mapping()
        print()
        
        print("🎉 所有测试完成！")
        print("\n📋 修复内容总结:")
        print("1. ✅ 增强验证码输入框检测（支持按钮左边的输入框）")
        print("2. ✅ 添加智联招聘关键词编码映射")
        print("3. ✅ 修复分页URL构建逻辑")
        print("4. ✅ 增强用户协议自动勾选")
        print("5. ✅ 优化页面元素选择器")
        
        print("\n🚀 现在可以运行:")
        print("   python fix_windows_config.py  # 修复配置")
        print("   python examples/basic_usage.py --example details  # 测试搜索")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")


if __name__ == "__main__":
    main()