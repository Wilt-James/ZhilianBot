#!/usr/bin/env python3
"""
只测试搜索功能，不访问详情页
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.login import ZhilianLogin
from modules.candidate import CandidateManager
from selenium.webdriver.common.by import By
from utils import log
import time


def wait_for_verification_code(driver):
    """等待用户输入验证码并自动提交登录"""
    try:
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
                
                # 首先检查是否已经登录成功
                current_url = driver.current_url
                if "login" not in current_url and "passport" not in current_url:
                    print("✅ 检测到已登录成功")
                    return True
                
                # 查找验证码输入框
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
                        input_elem = driver.find_element(By.XPATH, selector)
                        if input_elem.is_displayed():
                            code_input = input_elem
                            break
                    except:
                        continue
                
                if not code_input:
                    # 尝试查找所有文本输入框
                    all_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
                    visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]
                    
                    if len(visible_inputs) >= 2:
                        code_input = visible_inputs[1]  # 第二个通常是验证码
                    elif len(visible_inputs) == 1:
                        code_input = visible_inputs[0]
                
                if code_input:
                    try:
                        # 检查验证码输入（重新获取元素避免stale element）
                        fresh_code_input = None
                        for selector in code_input_selectors:
                            try:
                                input_elem = driver.find_element(By.XPATH, selector)
                                if input_elem.is_displayed():
                                    fresh_code_input = input_elem
                                    break
                            except:
                                continue
                        
                        if not fresh_code_input:
                            # 尝试查找所有文本输入框
                            all_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
                            visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]
                            if len(visible_inputs) >= 2:
                                fresh_code_input = visible_inputs[1]
                            elif len(visible_inputs) == 1:
                                fresh_code_input = visible_inputs[0]
                        
                        if fresh_code_input:
                            code_value = fresh_code_input.get_attribute('value') or ''
                            
                            if len(code_value) >= 4:
                                print(f"✅ 检测到验证码: {len(code_value)}位")
                                
                                # 等待用户输入完成
                                time.sleep(2)
                                
                                # 再次检查（再次重新获取元素）
                                final_fresh_input = None
                                for selector in code_input_selectors:
                                    try:
                                        input_elem = driver.find_element(By.XPATH, selector)
                                        if input_elem.is_displayed():
                                            final_fresh_input = input_elem
                                            break
                                    except:
                                        continue
                                
                                if final_fresh_input:
                                    final_code = final_fresh_input.get_attribute('value') or ''
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
                                                login_btn = driver.find_element(By.XPATH, selector)
                                                if login_btn.is_displayed() and login_btn.is_enabled():
                                                    driver.execute_script("arguments[0].click();", login_btn)
                                                    print(f"✅ 已点击登录按钮: {login_btn.text}")
                                                    login_clicked = True
                                                    break
                                            except:
                                                continue
                                        
                                        if not login_clicked:
                                            print("🔄 未找到登录按钮，尝试按回车键")
                                            try:
                                                from selenium.webdriver.common.keys import Keys
                                                final_fresh_input.send_keys(Keys.RETURN)
                                            except:
                                                print("按回车键失败")
                                        
                                        # 等待登录结果
                                        time.sleep(5)
                                        
                                        # 检查登录状态
                                        new_url = driver.current_url
                                        print(f"📄 登录后URL: {new_url}")
                                        
                                        if "login" not in new_url and "passport" not in new_url:
                                            print("🎉 登录成功！")
                                            return True
                                        else:
                                            print("❌ 登录可能失败，继续等待...")
                                            time.sleep(3)
                    except Exception as inner_e:
                        print(f"验证码处理内部错误: {inner_e}")
                        time.sleep(2)
                
                time.sleep(2)
                
            except Exception as e:
                print(f"检测过程出错: {e}")
                time.sleep(2)
        
        print("⏰ 等待超时")
        return False
        
    except Exception as e:
        print(f"❌ 验证码等待失败: {e}")
        return False


def test_search_only():
    """只测试搜索功能"""
    print("🔍 测试智联招聘搜索功能...")
    
    try:
        # 初始化登录管理器
        login_manager = ZhilianLogin()
        
        # 初始化候选人管理器
        candidate_manager = CandidateManager(login_manager.driver)
        
        print("✅ 浏览器初始化成功")
        
        # 登录 - 使用更智能的方式
        print("🔐 开始登录...")
        
        # 尝试自动登录
        login_success = False
        try:
            if login_manager.auto_login():
                print("✅ 自动登录成功")
                login_success = True
        except Exception as e:
            print(f"⚠️ 自动登录失败: {e}")
            print("尝试手动登录流程...")
        
        # 如果自动登录失败，尝试手动登录流程
        if not login_success:
            try:
                # 访问登录页面
                login_manager.driver.get("https://passport.zhaopin.com/login")
                time.sleep(3)
                
                # 手动输入手机号
                phone_number = "16621536193"
                phone_input = None
                
                phone_selectors = [
                    "//input[@placeholder='请输入手机号']",
                    "//input[@placeholder='手机号']",
                    "//input[contains(@class, 'phone')]",
                    "//input[@type='tel']"
                ]
                
                for selector in phone_selectors:
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
                    
                    time.sleep(2)
                    
                    # 勾选协议
                    try:
                        checkboxes = login_manager.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                        for checkbox in checkboxes:
                            if not checkbox.is_selected():
                                login_manager.driver.execute_script("arguments[0].click();", checkbox)
                                print("✅ 已勾选协议")
                                break
                    except:
                        pass
                    
                    time.sleep(2)
                    
                    # 尝试点击获取验证码（如果失败也继续）
                    try:
                        buttons = login_manager.driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            if "验证码" in button.text and button.is_displayed() and button.is_enabled():
                                login_manager.driver.execute_script("arguments[0].click();", button)
                                print(f"✅ 已点击: {button.text}")
                                break
                    except:
                        print("⚠️ 获取验证码按钮点击失败，继续等待验证码输入...")
                    
                    time.sleep(3)
                    
                    # 等待用户输入验证码
                    print("📱 请在浏览器中输入收到的验证码...")
                    print("程序将自动检测并提交...")
                    
                    # 使用成功的验证码检测逻辑
                    login_success = wait_for_verification_code(login_manager.driver)
                    if login_success:
                        print("✅ 手动登录成功")
                    else:
                        print("❌ 手动登录也失败")
                else:
                    print("❌ 未找到手机号输入框")
                    
            except Exception as e:
                print(f"❌ 手动登录过程失败: {e}")
        
        if not login_success:
            print("❌ 所有登录方式都失败")
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
        
        # 显示所有职位信息
        for i, candidate in enumerate(candidates, 1):
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
            candidate_manager.save_candidates_to_file(candidates, "search_only_results.json")
            print(f"\n💾 职位信息已保存到 search_only_results.json")
        
        print("\n🎉 搜索测试完成！")
        print("📊 统计信息:")
        print(f"   总职位数: {len(candidates)}")
        print(f"   有链接的职位: {len([c for c in candidates if c.get('profile_url')])}")
        print(f"   有薪资信息的职位: {len([c for c in candidates if c.get('salary') != '面议'])}")
        
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


if __name__ == "__main__":
    print("🚀 智联招聘搜索功能测试")
    print("=" * 50)
    print("注意：此测试只进行搜索，不访问职位详情页")
    print("=" * 50)
    
    test_search_only()