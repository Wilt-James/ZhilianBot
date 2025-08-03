#!/usr/bin/env python3
"""
创建正确的.env配置文件
"""

env_content = """# 智联招聘账号配置
ZHILIAN_USERNAME=16621536193
USERNAME=16621536193
PASSWORD=
LOGIN_TYPE=sms

# 浏览器配置
HEADLESS=false
BROWSER_TIMEOUT=30

# 中心服务器配置（可选）
# CENTER_SERVER_URL=http://your-center-server.com/api
# CENTER_SERVER_TOKEN=your_token_here

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
    print("🔧 登录方式已设置为: sms (短信验证码)")
    
    # 验证文件内容
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
        if '16621536193' in content:
            print("✅ 手机号配置验证成功")
        else:
            print("❌ 手机号配置验证失败")
            
except Exception as e:
    print(f"❌ 创建.env文件失败: {e}")
    print("请手动创建.env文件")