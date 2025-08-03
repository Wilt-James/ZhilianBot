#!/usr/bin/env python3
"""
智能登录测试脚本 - 处理各种登录场景
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.login import ZhilianLogin
from modules.candidate import CandidateManager
from selenium.webdriver.common.by import By
from utils import log


def smart_login_test():
    """智能登录测试"""
    print("🧠 智能登录测试...")
    
    try:
        # 初始化登录管理器
        login_manager = ZhilianLogin()
        print("✅ 浏览器初始化成功")
        
        # 访问登录页面
        print("🌐 访问登录页面...")
        login_manager.driver.get("https://passport.zhaopin.com/login")
        time.sleep(3)
        
        print(f"📄 当前页面: {login_manager.driver.title}")
        print(f"📄 当前URL: {login_manager.driver.current_url}")
        
        # 手动处理登录过程
        print("\n📱 开始登录过程...")
        
        # 1. 输入手机号
        phone_number = "16621536193"
        phone_input_selectors = [
            "//input[@placeholder='请输入手机号']",
            "//input[@placeholder='手机号']",
            "//input[contains(@class, 'phone')]",
            "//input[@type='tel']",
            "//input[@type='text'][1]"
        ]
        
        phone_input = None
        for selector in phone_input_selectors:
            try:
                phone_input = login_manager.driver.find_element(By.XPATH, selector)
                if phone_input.is_displayed():
                    break
            except:
                continue
        
        if phone_input:
            phone_input.clear()
            phone_input.send_keys(phone_number)
            print(f"✅ 已输入手机号: {phone_number}")
        else:
            print("❌ 未找到手机号输入框")
            return False
        
        time.sleep(2)
        
        # 2. 勾选协议
        print("📋 勾选用户协议...")
        try:
            checkboxes = login_manager.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            for checkbox in checkboxes:
                if not checkbox.is_selected():
                    login_manager.driver.execute_script("arguments[0].click();", checkbox)
                    print("✅ 已勾选协议")
                    break
        except Exception as e:
            print(f"勾选协议失败: {e}")
        
        time.sleep(2)
        
        # 3. 尝试点击获取验证码
        print("🔘 尝试点击获取验证码...")
        sms_button_clicked = False
        
        sms_button_selectors = [
            "//button[contains(text(), '获取验证码')]",
            "//button[contains(text(), '发送验证码')]",
            "//button[contains(text(), '获取短信验证码')]",
            "//a[contains(text(), '获取验证码')]"
        ]
        
        for selector in sms_button_selectors:
            try:
                button = login_manager.driver.find_element(By.XPATH, selector)
                if button.is_displayed() and button.is_enabled():
                    login_manager.driver.execute_script("arguments[0].click();", button)
                    print(f"✅ 已点击获取验证码按钮: {button.text}")
                    sms_button_clicked = True
                    break
            except:
                continue
        
        if not sms_button_clicked:
            print("⚠️ 未找到获取验证码按钮，可能已经发送过或页面结构不同")
            print("继续查找验证码输入框...")
        
        time.sleep(3)
        
        # 4. 查找验证码输入框
        print("🔍 查找验证码输入框...")
        
        code_input_selectors = [
            "//input[@placeholder='请输入验证码']",
            "//input[@placeholder='验证码']",
            "//input[contains(@class, 'code')]",
            "//input[contains(@class, 'verify')]",
            "//input[@maxlength='4' or @maxlength='6']",
            "//input[@type='text'][contains(@name, 'code')]"
        ]
        
        code_input = None
        for selector in code_input_selectors:
            try:
                input_elem = login_manager.driver.find_element(By.XPATH, selector)
                if input_elem.is_displayed():
                    code_input = input_elem
                    print(f"✅ 找到验证码输入框: {selector}")
                    break
            except:
                continue
        
        if not code_input:
            # 尝试查找所有文本输入框
            all_inputs = login_manager.driver.find_elements(By.XPATH, "//input[@type='text']")
            visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]
            
            print(f"🔍 找到 {len(visible_inputs)} 个可见的文本输入框")
            
            if len(visible_inputs) >= 2:
                code_input = visible_inputs[1]  # 第二个通常是验证码
                print("✅ 使用第二个输入框作为验证码框")
            elif len(visible_inputs) == 1:
                code_input = visible_inputs[0]
                print("✅ 使用唯一输入框作为验证码框")
        
        if not code_input:
            print("❌ 未找到验证码输入框")
            return False
        
        # 5. 等待用户输入验证码
        print("\n📱 请在浏览器中输入收到的验证码...")
        print("程序将自动检测验证码输入并尝试登录...")
        
        start_time = time.time()
        max_wait = 120  # 2分钟
        last_log = 0
        
        while time.time() - start_time < max_wait:
            try:
                current_time = time.time()
                
                # 每30秒输出状态
                if current_time - last_log > 30:
                    remaining = int(max_wait - (current_time - start_time))
                    print(f"⏳ 等待验证码输入... 剩余时间: {remaining}秒")
                    last_log = current_time
                
                # 检查验证码输入
                code_value = code_input.get_attribute('value') or ''
                
                if len(code_value) >= 4:
                    print(f"✅ 检测到验证码: {len(code_value)}位")
                    
                    # 等待用户输入完成
                    time.sleep(2)
                    
                    # 再次检查
                    final_code = code_input.get_attribute('value') or ''
                    if len(final_code) >= 4:
                        print("🎯 尝试提交登录...")
                        
                        # 查找登录按钮
                        login_button_selectors = [
                            "//button[contains(text(), '登录')]",
                            "//button[contains(text(), '立即登录')]",
                            "//button[@type='submit']",
                            "//input[@type='submit']"
                        ]
                        
                        login_clicked = False
                        for selector in login_button_selectors:
                            try:
                                login_btn = login_manager.driver.find_element(By.XPATH, selector)
                                if login_btn.is_displayed() and login_btn.is_enabled():
                                    login_manager.driver.execute_script("arguments[0].click();", login_btn)
                                    print(f"✅ 已点击登录按钮: {login_btn.text}")
                                    login_clicked = True
                                    break
                            except:
                                continue
                        
                        if not login_clicked:
                            print("🔄 未找到登录按钮，尝试按回车键")
                            from selenium.webdriver.common.keys import Keys
                            code_input.send_keys(Keys.RETURN)
                        
                        # 等待登录结果
                        time.sleep(5)
                        
                        # 检查登录状态
                        current_url = login_manager.driver.current_url
                        print(f"📄 登录后URL: {current_url}")
                        
                        if "login" not in current_url and "passport" not in current_url:
                            print("🎉 登录成功！")
                            
                            # 测试搜索功能
                            print("\n🔍 开始测试搜索功能...")
                            candidate_manager = CandidateManager(login_manager.driver)
                            
                            search_params = {
                                'keyword': 'Java开发',
                                'location': '北京',
                                'page_limit': 1
                            }
                            
                            candidates = candidate_manager.search_candidates(**search_params)
                            print(f"🎯 搜索完成，找到 {len(candidates)} 个职位")
                            
                            # 显示前几个职位
                            for i, candidate in enumerate(candidates[:5], 1):
                                print(f"📋 职位 {i}: {candidate.get('name', '未知')} - {candidate.get('company', '未知')} - {candidate.get('salary', '未知')}")
                            
                            return True
                        else:
                            print("❌ 登录可能失败，继续等待...")
                            time.sleep(3)
                
                time.sleep(2)
                
            except Exception as e:
                print(f"检测过程出错: {e}")
                time.sleep(2)
        
        print("⏰ 等待超时")
        return False
        
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
    print("🧠 智能登录+搜索测试")
    print("=" * 50)
    print("此脚本会智能处理各种登录场景")
    print("即使获取验证码按钮失败也会继续尝试")
    print("=" * 50)
    
    success = smart_login_test()
    
    if success:
        print("\n🎉 测试完全成功！")
    else:
        print("\n❌ 测试失败")
    
    print("\n✨ 测试结束")