#!/usr/bin/env python3
"""
修复Windows系统下的配置问题
解决USERNAME环境变量冲突
"""
import os
import sys

def create_env_file():
    """创建正确的.env文件"""
    
    # Windows专用配置，避免USERNAME冲突
    env_content = """# 智联招聘账号配置（Windows专用）
ZHILIAN_USERNAME=16621536193
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

# 中心服务器配置（可选）
# CENTER_SERVER_URL=http://your-center-server.com/api
# CENTER_SERVER_TOKEN=your_token_here
"""

    try:
        # 检查当前目录
        current_dir = os.getcwd()
        print(f"📁 当前工作目录: {current_dir}")
        
        # 创建.env文件
        env_path = os.path.join(current_dir, '.env')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ .env文件已创建: {env_path}")
        
        # 验证文件内容
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'ZHILIAN_USERNAME=16621536193' in content:
                print("✅ 手机号配置验证成功: 16621536193")
            else:
                print("❌ 手机号配置验证失败")
                return False
        
        # 检查系统环境变量冲突
        system_username = os.environ.get('USERNAME', '')
        if system_username:
            print(f"⚠️  检测到系统USERNAME环境变量: {system_username}")
            print("✅ 已使用ZHILIAN_USERNAME避免冲突")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建.env文件失败: {e}")
        return False

def test_config():
    """测试配置是否正确"""
    try:
        # 临时测试配置读取
        from dotenv import load_dotenv
        load_dotenv()
        
        zhilian_username = os.environ.get('ZHILIAN_USERNAME')
        username = os.environ.get('USERNAME')
        
        print("\n🔍 配置测试结果:")
        print(f"ZHILIAN_USERNAME: {zhilian_username}")
        print(f"系统USERNAME: {username}")
        
        if zhilian_username == '16621536193':
            print("✅ 智联招聘手机号配置正确")
            return True
        else:
            print("❌ 智联招聘手机号配置错误")
            return False
            
    except ImportError:
        print("⚠️  python-dotenv未安装，跳过配置测试")
        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def main():
    print("🔧 Windows系统配置修复工具")
    print("=" * 50)
    
    # 1. 创建配置文件
    if create_env_file():
        print("\n✅ 步骤1: .env文件创建成功")
    else:
        print("\n❌ 步骤1: .env文件创建失败")
        return
    
    # 2. 测试配置
    if test_config():
        print("\n✅ 步骤2: 配置测试通过")
    else:
        print("\n❌ 步骤2: 配置测试失败")
    
    print("\n🚀 修复完成！现在可以运行:")
    print("   python examples/basic_usage.py --example details")
    print("\n📱 预期日志应显示:")
    print("   已输入手机号: 16621536193")
    print("   已勾选用户服务协议")
    print("   已点击获取验证码按钮")
    print("\n⚠️  注意事项:")
    print("   1. 程序会自动勾选用户协议")
    print("   2. 需要手动输入收到的短信验证码")
    print("   3. 搜索功能已适配智联招聘最新页面结构")

if __name__ == "__main__":
    main()