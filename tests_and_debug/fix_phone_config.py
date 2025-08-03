#!/usr/bin/env python3
"""
修复手机号配置问题的快速脚本
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings


def fix_phone_config():
    """修复手机号配置问题"""
    print("🔧 检查手机号配置...")
    
    # 检查当前配置
    zhilian_username = getattr(settings, 'ZHILIAN_USERNAME', None)
    username = getattr(settings, 'USERNAME', None)
    
    print(f"ZHILIAN_USERNAME: {zhilian_username}")
    print(f"USERNAME: {username}")
    
    # 如果都没有配置，创建.env文件
    if not zhilian_username and not username:
        print("❌ 未找到手机号配置")
        print("🔧 正在创建.env文件...")
        
        env_content = """# 智联招聘账号配置
ZHILIAN_USERNAME=16621536193
USERNAME=16621536193
PASSWORD=
LOGIN_TYPE=sms

# 浏览器配置
HEADLESS=false
BROWSER_TIMEOUT=30

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=zhilian_bot.log

# 其他配置
REQUEST_DELAY=1.0
MAX_RETRY_ATTEMPTS=3
"""
        
        try:
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(env_content)
            print("✅ .env文件创建成功！")
            print("📱 手机号已设置为: 16621536193")
            print("🔄 请重新运行程序以加载新配置")
            return True
        except Exception as e:
            print(f"❌ 创建.env文件失败: {e}")
            return False
    else:
        phone_number = zhilian_username or username
        print(f"✅ 找到手机号配置: {phone_number}")
        return True


def test_login_with_config():
    """测试使用当前配置登录"""
    print("\n🧪 测试稳定登录...")
    
    try:
        from modules.login import ZhilianLogin
        
        login_manager = ZhilianLogin()
        print("✅ 浏览器初始化成功")
        
        # 测试稳定登录
        success = login_manager.login_with_sms_robust()
        
        if success:
            print("🎉 稳定登录测试成功！")
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


if __name__ == "__main__":
    print("🔧 手机号配置修复工具")
    print("=" * 40)
    
    # 修复配置
    if fix_phone_config():
        print("\n" + "=" * 40)
        choice = input("是否立即测试登录？(y/n): ").lower().strip()
        
        if choice == 'y':
            test_login_with_config()
        else:
            print("✅ 配置修复完成，您现在可以运行:")
            print("python examples/basic_usage.py --robust --example search")
    else:
        print("❌ 配置修复失败")
        print("请手动创建.env文件并设置ZHILIAN_USERNAME=您的手机号")