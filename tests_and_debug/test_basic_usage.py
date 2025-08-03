#!/usr/bin/env python3
"""
测试修改后的basic_usage.py
"""
import sys
import os
import subprocess
import time

def test_basic_usage_search():
    """测试basic_usage.py的search示例"""
    print("🧪 测试 basic_usage.py --example search")
    print("=" * 50)
    
    try:
        # 运行basic_usage.py
        cmd = [sys.executable, "examples/basic_usage.py", "--example", "search"]
        print(f"🚀 执行命令: {' '.join(cmd)}")
        
        # 启动进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("📱 程序已启动，请在浏览器中完成登录...")
        print("⏳ 实时输出:")
        print("-" * 30)
        
        # 实时显示输出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # 等待进程结束
        return_code = process.wait()
        
        print("-" * 30)
        print(f"📊 进程结束，返回码: {return_code}")
        
        if return_code == 0:
            print("✅ 测试成功完成！")
        else:
            print("❌ 测试失败")
        
        return return_code == 0
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False


def test_login_module_directly():
    """直接测试登录模块"""
    print("\n🔍 直接测试登录模块...")
    
    try:
        # 添加项目路径
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from modules.login import ZhilianLogin
        
        # 初始化登录管理器
        login_manager = ZhilianLogin()
        print("✅ 登录管理器初始化成功")
        
        # 尝试登录
        print("🔐 开始登录测试...")
        if login_manager.auto_login():
            print("✅ 登录成功！")
            
            # 检查登录状态
            if login_manager.check_login_status():
                print("✅ 登录状态验证成功")
            else:
                print("❌ 登录状态验证失败")
            
            return True
        else:
            print("❌ 登录失败")
            return False
            
    except Exception as e:
        print(f"❌ 直接测试失败: {e}")
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
    print("🧪 Basic Usage 测试工具")
    print("=" * 50)
    
    choice = input("选择测试方式:\n1. 测试完整的basic_usage.py\n2. 直接测试登录模块\n请输入 1 或 2: ").strip()
    
    if choice == "1":
        success = test_basic_usage_search()
    elif choice == "2":
        success = test_login_module_directly()
    else:
        print("无效选择")
        success = False
    
    if success:
        print("\n🎉 测试成功！")
    else:
        print("\n❌ 测试失败")
    
    print("\n✨ 测试结束")