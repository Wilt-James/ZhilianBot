# 智联招聘自动化工具

一个功能强大的智联招聘自动化工具，支持自动登录、候选人搜索、打招呼、实时聊天和消息转发等功能。

## 功能特性

### 🔐 自动登录
- 支持手机短信验证码登录（主要方式）
- 支持二维码扫码登录
- 自动检测登录状态
- 智能检测验证码输入

### 🔍 候选人搜索
- 多条件搜索候选人
- 支持关键词、地点、经验、学历等筛选
- 批量获取候选人基本信息
- 详细简历信息提取

### 💬 智能互动
- 自动发送打招呼消息
- 支持自定义消息模板
- 批量打招呼功能
- 智能延迟避免检测

### 🌐 实时聊天
- WebSocket实时聊天连接
- 自动消息监控
- 聊天历史获取
- 消息状态跟踪

### 📡 消息转发
- 实时转发消息到中心服务器
- 支持批量消息处理
- 自动重连机制
- 完整的错误处理

## 安装说明

### 环境要求
- Python 3.7+
- Chrome浏览器
- 稳定的网络连接

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd zhilian-recruitment-bot
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
# 复制配置文件模板
cp env_example.txt .env

# 编辑配置文件
vim .env
```

4. 配置参数
```bash
# 智联招聘账号配置
USERNAME=16621536193  # 手机号
PASSWORD=  # 已废弃，智联招聘现在只支持手机验证码登录
LOGIN_TYPE=sms  # sms（短信验证码）或 qrcode（二维码扫码）

# 浏览器配置
HEADLESS=false
BROWSER_TIMEOUT=30

# 中心服务器配置（可选）
CENTER_SERVER_URL=http://your-center-server.com/api
CENTER_SERVER_TOKEN=your_token_here

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=zhilian_bot.log
```

## 使用方法

### 基本使用

#### 1. 运行完整机器人
```bash
python zhilian_bot.py
```

#### 2. 基本示例
```bash
# 搜索并打招呼
python examples/basic_usage.py --example search

# 监控聊天消息
python examples/basic_usage.py --example monitor

# 获取候选人详细信息
python examples/basic_usage.py --example details
```

#### 3. 高级示例
```bash
# 自定义消息处理器
python examples/advanced_usage.py --example handler

# 批量操作
python examples/advanced_usage.py --example batch

# 消息转发功能
python examples/advanced_usage.py --example forwarding

# 完整工作流程
python examples/advanced_usage.py --example workflow
```

### 编程接口

#### 初始化机器人
```python
from zhilian_bot import ZhilianBot

bot = ZhilianBot()

# 初始化和登录
if bot.initialize() and bot.login():
    print("机器人启动成功")
```

#### 搜索候选人
```python
# 搜索参数
search_params = {
    'keyword': 'Python开发工程师',
    'location': '北京',
    'experience': '3-5年',
    'education': '本科',
    'page_limit': 3
}

# 执行搜索
candidates = bot.candidate_manager.search_candidates(**search_params)
print(f"找到 {len(candidates)} 个候选人")
```

#### 批量打招呼
```python
# 自定义消息
greeting_message = "您好，我们公司有很好的职位机会，想和您聊聊。"

# 批量打招呼
results = bot.interaction_manager.batch_greeting(
    candidates=candidates,
    message_template=greeting_message,
    max_count=20
)

print(f"发送结果: 成功 {results['success']}, 失败 {results['failed']}")
```

#### 监控聊天
```python
# 启动WebSocket聊天
bot.start_websocket_chat()

# 获取聊天列表
chat_list = bot.websocket_manager.get_chat_list()

# 监控新消息
for chat in chat_list:
    if chat.get('unread_count', 0) > 0:
        messages = bot.websocket_manager.get_chat_history(chat['id'])
        print(f"新消息: {messages}")
```

#### 消息转发
```python
# 启动消息转发服务
bot.start_message_forwarding()

# 转发候选人信息
bot.message_forwarder.forward_candidate_info(candidate_data)

# 转发聊天消息
bot.message_forwarder.forward_chat_message(
    sender_id='candidate_001',
    recipient_id='hr_001',
    content='消息内容'
)
```

## 项目结构

```
zhilian-recruitment-bot/
├── zhilian_bot.py          # 主程序
├── config.py               # 配置管理
├── requirements.txt        # 依赖包
├── env_example.txt         # 配置文件模板
├── README.md              # 说明文档
├── modules/               # 核心模块
│   ├── __init__.py
│   ├── login.py           # 登录模块
│   ├── candidate.py       # 候选人管理
│   ├── interaction.py     # 互动功能
│   ├── websocket_chat.py  # WebSocket聊天
│   └── message_forwarder.py # 消息转发
├── utils/                 # 工具模块
│   ├── __init__.py
│   └── logger.py          # 日志工具
└── examples/              # 示例代码
    ├── basic_usage.py     # 基本使用示例
    └── advanced_usage.py  # 高级使用示例
```

## 核心模块说明

### 登录模块 (login.py)
- `ZhilianLogin`: 处理智联招聘的自动登录
- 支持密码登录和二维码登录
- 自动处理验证码和登录状态检查

### 候选人管理 (candidate.py)
- `CandidateManager`: 候选人搜索和信息提取
- 多条件搜索功能
- 详细简历信息获取
- 数据保存和加载

### 互动功能 (interaction.py)
- `InteractionManager`: 处理与候选人的互动
- 自动打招呼功能
- 批量消息发送
- 消息状态跟踪

### WebSocket聊天 (websocket_chat.py)
- `WebSocketChatManager`: 实时聊天功能
- WebSocket连接管理
- 消息监控和处理
- 自动重连机制

### 消息转发 (message_forwarder.py)
- `MessageForwarder`: 消息转发到中心服务器
- 批量消息处理
- 错误重试机制
- 远程命令执行

## 配置说明

### 基本配置
- `USERNAME/PASSWORD`: 智联招聘账号
- `LOGIN_TYPE`: 登录方式 (password/qrcode)
- `HEADLESS`: 是否无头模式运行浏览器

### 高级配置
- `CENTER_SERVER_URL`: 中心服务器地址
- `CENTER_SERVER_TOKEN`: 认证令牌
- `REQUEST_DELAY`: 请求间隔时间
- `MAX_RETRY_ATTEMPTS`: 最大重试次数

## 注意事项

### 使用建议
1. **合理控制频率**: 避免过于频繁的操作被系统检测
2. **遵守平台规则**: 确保使用符合智联招聘的服务条款
3. **数据安全**: 妥善保管账号信息和候选人数据
4. **监控日志**: 定期查看日志文件排查问题

### 常见问题
1. **登录失败**: 检查账号密码，可能需要手动处理验证码
2. **搜索无结果**: 调整搜索条件，检查网络连接
3. **WebSocket连接失败**: 确保网络稳定，检查防火墙设置
4. **消息转发失败**: 检查中心服务器配置和网络连接

### 法律声明
本工具仅供学习和研究使用，使用者需要：
- 遵守智联招聘的服务条款
- 尊重候选人隐私
- 合法合规使用数据
- 承担使用风险

## 技术支持

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 技术交流群

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现基本的登录、搜索、打招呼功能
- 支持WebSocket实时聊天
- 添加消息转发功能

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。