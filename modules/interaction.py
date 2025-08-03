"""
候选人互动模块 - 打招呼、发送消息等
"""
import time
import random
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import settings
from utils import log


class InteractionManager:
    """候选人互动管理类"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.BROWSER_TIMEOUT)
        
        # 预设的打招呼模板
        self.greeting_templates = [
            "您好，我是{company}的HR，看到您的简历很符合我们的职位要求，想和您聊聊。",
            "您好，我们公司有个{position}的职位很适合您，不知道您是否有兴趣了解一下？",
            "您好，看到您在{skill}方面的经验很丰富，我们正好有个相关的职位机会。",
            "您好，我是{company}的招聘负责人，您的背景很符合我们的需求，方便聊聊吗？",
            "您好，我们是一家{industry}公司，看到您的简历很优秀，想邀请您了解一下我们的职位。"
        ]
    
    def send_greeting(self, 
                     candidate_url: str, 
                     message: str = None,
                     company: str = "我们公司",
                     position: str = "相关职位",
                     skill: str = "技术",
                     industry: str = "互联网") -> bool:
        """
        向候选人发送打招呼消息
        
        Args:
            candidate_url: 候选人详情页URL
            message: 自定义消息，如果为空则使用模板
            company: 公司名称
            position: 职位名称
            skill: 技能关键词
            industry: 行业类型
            
        Returns:
            是否发送成功
        """
        try:
            log.info(f"向候选人发送打招呼: {candidate_url}")
            
            # 访问候选人详情页
            self.driver.get(candidate_url)
            time.sleep(settings.REQUEST_DELAY)
            
            # 查找并点击"打招呼"或"沟通"按钮
            if not self._click_contact_button():
                log.error("未找到联系按钮")
                return False
            
            # 等待消息输入框出现
            if not self._wait_for_message_input():
                log.error("消息输入框未出现")
                return False
            
            # 生成或使用自定义消息
            if not message:
                message = self._generate_greeting_message(
                    company=company,
                    position=position,
                    skill=skill,
                    industry=industry
                )
            
            # 输入消息
            if not self._input_message(message):
                log.error("输入消息失败")
                return False
            
            # 发送消息
            if not self._send_message():
                log.error("发送消息失败")
                return False
            
            log.info("打招呼消息发送成功")
            return True
            
        except Exception as e:
            log.error(f"发送打招呼失败: {e}")
            return False
    
    def _click_contact_button(self) -> bool:
        """点击联系按钮"""
        try:
            # 尝试多种可能的按钮文本和类名
            button_selectors = [
                "//button[contains(text(), '打招呼')]",
                "//button[contains(text(), '沟通')]",
                "//button[contains(text(), '联系')]",
                "//a[contains(text(), '打招呼')]",
                "//a[contains(text(), '沟通')]",
                ".contact-btn",
                ".greeting-btn",
                ".chat-btn"
            ]
            
            for selector in button_selectors:
                try:
                    if selector.startswith("//"):
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    button.click()
                    time.sleep(1)
                    return True
                    
                except TimeoutException:
                    continue
                except Exception as e:
                    log.debug(f"尝试点击按钮失败: {selector}, {e}")
                    continue
            
            return False
            
        except Exception as e:
            log.error(f"点击联系按钮失败: {e}")
            return False
    
    def _wait_for_message_input(self) -> bool:
        """等待消息输入框出现"""
        try:
            # 尝试多种可能的输入框选择器
            input_selectors = [
                "textarea[placeholder*='消息']",
                "textarea[placeholder*='打招呼']",
                "textarea[placeholder*='沟通']",
                ".message-input",
                ".chat-input",
                "textarea.form-control",
                "#messageContent",
                "textarea[name='content']"
            ]
            
            for selector in input_selectors:
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    return True
                except TimeoutException:
                    continue
            
            return False
            
        except Exception as e:
            log.error(f"等待消息输入框失败: {e}")
            return False
    
    def _generate_greeting_message(self, **kwargs) -> str:
        """生成打招呼消息"""
        try:
            template = random.choice(self.greeting_templates)
            message = template.format(**kwargs)
            return message
        except Exception as e:
            log.error(f"生成打招呼消息失败: {e}")
            return "您好，看到您的简历很优秀，想和您聊聊相关的职位机会。"
    
    def _input_message(self, message: str) -> bool:
        """输入消息"""
        try:
            # 查找消息输入框
            input_selectors = [
                "textarea[placeholder*='消息']",
                "textarea[placeholder*='打招呼']",
                "textarea[placeholder*='沟通']",
                ".message-input",
                ".chat-input",
                "textarea.form-control",
                "#messageContent",
                "textarea[name='content']"
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    input_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if input_element.is_displayed():
                        break
                except:
                    continue
            
            if not input_element:
                log.error("未找到消息输入框")
                return False
            
            # 清空并输入消息
            input_element.clear()
            input_element.send_keys(message)
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            log.error(f"输入消息失败: {e}")
            return False
    
    def _send_message(self) -> bool:
        """发送消息"""
        try:
            # 尝试多种可能的发送按钮
            send_selectors = [
                "//button[contains(text(), '发送')]",
                "//button[contains(text(), '确定')]",
                "//button[contains(text(), '提交')]",
                ".send-btn",
                ".submit-btn",
                ".confirm-btn",
                "button[type='submit']"
            ]
            
            for selector in send_selectors:
                try:
                    if selector.startswith("//"):
                        button = self.driver.find_element(By.XPATH, selector)
                    else:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        time.sleep(1)
                        return True
                        
                except:
                    continue
            
            # 如果没有找到发送按钮，尝试按回车键
            try:
                input_element = self.driver.find_element(By.CSS_SELECTOR, "textarea")
                input_element.send_keys(Keys.RETURN)
                time.sleep(1)
                return True
            except:
                pass
            
            return False
            
        except Exception as e:
            log.error(f"发送消息失败: {e}")
            return False
    
    def batch_greeting(self, 
                      candidates: List[Dict], 
                      message_template: str = None,
                      delay_range: tuple = (3, 8),
                      max_count: int = 50) -> Dict:
        """
        批量发送打招呼消息
        
        Args:
            candidates: 候选人列表
            message_template: 消息模板
            delay_range: 发送间隔范围（秒）
            max_count: 最大发送数量
            
        Returns:
            发送结果统计
        """
        try:
            log.info(f"开始批量发送打招呼，候选人数量: {len(candidates)}")
            
            results = {
                'total': 0,
                'success': 0,
                'failed': 0,
                'details': []
            }
            
            count = 0
            for candidate in candidates:
                if count >= max_count:
                    log.info(f"已达到最大发送数量限制: {max_count}")
                    break
                
                try:
                    profile_url = candidate.get('profile_url', '')
                    if not profile_url:
                        log.warning(f"候选人 {candidate.get('name', '未知')} 没有详情页URL")
                        continue
                    
                    # 发送打招呼
                    success = self.send_greeting(
                        candidate_url=profile_url,
                        message=message_template,
                        company=candidate.get('company', '我们公司'),
                        position=candidate.get('name', '相关职位')
                    )
                    
                    result_detail = {
                        'name': candidate.get('name', '未知'),
                        'company': candidate.get('company', '未知'),
                        'url': profile_url,
                        'success': success,
                        'timestamp': time.time()
                    }
                    
                    results['details'].append(result_detail)
                    results['total'] += 1
                    
                    if success:
                        results['success'] += 1
                        log.info(f"成功向 {candidate.get('name', '未知')} 发送打招呼")
                    else:
                        results['failed'] += 1
                        log.warning(f"向 {candidate.get('name', '未知')} 发送打招呼失败")
                    
                    count += 1
                    
                    # 随机延迟，避免被检测
                    delay = random.uniform(delay_range[0], delay_range[1])
                    log.debug(f"等待 {delay:.1f} 秒后继续...")
                    time.sleep(delay)
                    
                except Exception as e:
                    log.error(f"处理候选人 {candidate.get('name', '未知')} 时出错: {e}")
                    results['failed'] += 1
                    continue
            
            log.info(f"批量发送完成，总数: {results['total']}, 成功: {results['success']}, 失败: {results['failed']}")
            return results
            
        except Exception as e:
            log.error(f"批量发送打招呼失败: {e}")
            return {'total': 0, 'success': 0, 'failed': 0, 'details': []}
    
    def check_message_status(self, candidate_url: str) -> Dict:
        """检查消息状态"""
        try:
            self.driver.get(candidate_url)
            time.sleep(settings.REQUEST_DELAY)
            
            status = {
                'has_replied': False,
                'last_message': '',
                'message_count': 0,
                'last_active': ''
            }
            
            # 这里需要根据智联招聘的实际页面结构来实现
            # 检查是否有回复、最后消息内容等
            
            return status
            
        except Exception as e:
            log.error(f"检查消息状态失败: {e}")
            return {}
    
    def get_conversation_history(self, candidate_url: str) -> List[Dict]:
        """获取对话历史"""
        try:
            self.driver.get(candidate_url)
            time.sleep(settings.REQUEST_DELAY)
            
            messages = []
            
            # 这里需要根据智联招聘的实际页面结构来实现
            # 获取对话历史记录
            
            return messages
            
        except Exception as e:
            log.error(f"获取对话历史失败: {e}")
            return []
    
    def send_follow_up_message(self, candidate_url: str, message: str) -> bool:
        """发送跟进消息"""
        try:
            log.info(f"发送跟进消息: {candidate_url}")
            
            # 访问对话页面
            self.driver.get(candidate_url)
            time.sleep(settings.REQUEST_DELAY)
            
            # 输入并发送消息
            if self._input_message(message) and self._send_message():
                log.info("跟进消息发送成功")
                return True
            else:
                log.error("跟进消息发送失败")
                return False
                
        except Exception as e:
            log.error(f"发送跟进消息失败: {e}")
            return False