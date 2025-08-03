#!/usr/bin/env python3
"""
测试新的稳定登录逻辑
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.login import ZhilianLogin
from utils import log


def test_new_robust_login():
    """测试新的稳定登录逻辑"""
    print("🛡️ 测试新的稳定登录逻辑...")
    
    try:
        # 初始化
        login_manager = ZhilianLogin()
        print("✅ 浏览器初始化成功")
        
        # 测试稳定登录
        success = login_manager.login_with_sms_robust()
        
        if success:
            print("🎉 稳定登录测试成功！")
            
            # 验证登录状态
            if login_manager.is_logged_in():
                print("✅ 登录状态验证成功")
            else:
                print("❌ 登录状态验证失败")
                
        else:
            print("❌ 稳定登录测试失败")
            
        return success
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            login_manager.close()
            print("🔒 浏览器已关闭")
        except:
            pass


def test_auto_login_with_robust():
    """测试auto_login方法（现在使用稳定版本）"""
    print("\n🔄 测试auto_login方法（稳定版本）...")
    
    try:
        # 初始化
        login_manager = ZhilianLogin()
        print("✅ 浏览器初始化成功")
        
        # 测试auto_login（现在内部使用稳定版本）
        success = login_manager.auto_login()
        
        if success:
            print("🎉 auto_login测试成功！")
            
            # 验证登录状态
            if login_manager.is_logged_in():
                print("✅ 登录状态验证成功")
            else:
                print("❌ 登录状态验证失败")
                
        else:
            print("❌ auto_login测试失败")
            
        return success
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            login_manager.close()
            print("🔒 浏览器已关闭")
        except:
            pass


if __name__ == "__main__":
    print("🛡️ 新稳定登录逻辑测试")
    print("=" * 50)
    print("测试集成到modules/login.py中的稳定登录逻辑")
    print("=" * 50)
    
    # 测试1：直接测试稳定登录方法
    print("\n📋 测试1: 直接测试login_with_sms_robust方法")
    success1 = test_new_robust_login()
    
    if success1:
        print("\n✅ 测试1通过，继续测试2...")
        
        # 等待用户确认
        input("\n按回车键继续测试auto_login方法...")
        
        # 测试2：测试auto_login方法
        print("\n📋 测试2: 测试auto_login方法（现在使用稳定版本）")
        success2 = test_auto_login_with_robust()
        
        if success2:
            print("\n🎉 所有测试通过！")
            print("✅ 稳定登录逻辑已成功集成到系统中")
        else:
            print("\n❌ 测试2失败")
    else:
        print("\n❌ 测试1失败，跳过后续测试")
    
    print("\n✨ 测试结束")