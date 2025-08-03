#!/usr/bin/env python3
"""
修复版搜索测试脚本 - 使用成功的登录逻辑
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.login import ZhilianLogin
from modules.candidate import CandidateManager
from selenium.webdriver.common.by import By
from utils import log


def test_search_with_fixed_login():
    """使用修复的登录逻辑进行搜索测试"""
    print("🔍 测试智联招聘搜索功能（修复版）...")
    
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
        
        # 手动处理登录过程（复制成功的逻辑）
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
                
                # 首先检查是否已经登录成功
                current_url = login_manager.driver.current_url
                if "login" not in current_url and "passport" not in current_url:
                    print("🎉 检测到已登录成功！")
                    break
                
                # 重新查找验证码输入框（避免stale element）
                current_code_input = None
                for selector in code_input_selectors:
                    try:
                        input_elem = login_manager.driver.find_element(By.XPATH, selector)
                        if input_elem.is_displayed():
                            current_code_input = input_elem
                            break
                    except:
                        continue
                
                if not current_code_input:
                    # 尝试查找所有文本输入框
                    try:
                        all_inputs = login_manager.driver.find_elements(By.XPATH, "//input[@type='text']")
                        visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]
                        
                        if len(visible_inputs) >= 2:
                            current_code_input = visible_inputs[1]  # 第二个通常是验证码
                        elif len(visible_inputs) == 1:
                            current_code_input = visible_inputs[0]
                    except:
                        pass
                
                if current_code_input:
                    try:
                        # 检查验证码输入
                        code_value = current_code_input.get_attribute('value') or ''
                        
                        if len(code_value) >= 4:
                            print(f"✅ 检测到验证码: {len(code_value)}位")
                            
                            # 等待用户输入完成
                            time.sleep(2)
                            
                            # 再次检查（重新获取元素）
                            fresh_code_input = None
                            for selector in code_input_selectors:
                                try:
                                    input_elem = login_manager.driver.find_element(By.XPATH, selector)
                                    if input_elem.is_displayed():
                                        fresh_code_input = input_elem
                                        print(f"🔍 重新找到验证码输入框: {selector}")
                                        break
                                except:
                                    continue
                            
                            # 如果重新获取失败，使用原来的输入框
                            if not fresh_code_input:
                                fresh_code_input = current_code_input
                                print("⚠️ 重新获取验证码输入框失败，使用原输入框")
                            
                            if fresh_code_input:
                                try:
                                    final_code = fresh_code_input.get_attribute('value') or ''
                                    print(f"🔍 最终验证码长度: {len(final_code)}位")
                                    
                                    if len(final_code) >= 4:
                                        print("🎯 尝试提交登录...")
                                        
                                        # 查找登录按钮
                                        login_button_selectors = [
                                            "//button[contains(text(), '登录')]",
                                            "//button[contains(text(), '立即登录')]",
                                            "//button[contains(text(), '确认登录')]",
                                            "//button[@type='submit']",
                                            "//input[@type='submit']",
                                            "//a[contains(text(), '登录')]"
                                        ]
                                        
                                        print("🔍 查找登录按钮...")
                                        login_clicked = False
                                        for i, selector in enumerate(login_button_selectors):
                                            try:
                                                login_btn = login_manager.driver.find_element(By.XPATH, selector)
                                                if login_btn.is_displayed() and login_btn.is_enabled():
                                                    print(f"🎯 找到登录按钮 {i+1}: {login_btn.text}")
                                                    login_manager.driver.execute_script("arguments[0].click();", login_btn)
                                                    print(f"✅ 已点击登录按钮: {login_btn.text}")
                                                    login_clicked = True
                                                    break
                                                else:
                                                    print(f"❌ 按钮 {i+1} 不可用: displayed={login_btn.is_displayed()}, enabled={login_btn.is_enabled()}")
                                            except Exception as btn_e:
                                                print(f"❌ 按钮选择器 {i+1} 失败: {btn_e}")
                                                continue
                                        
                                        if not login_clicked:
                                            print("🔄 未找到登录按钮，尝试按回车键")
                                            try:
                                                from selenium.webdriver.common.keys import Keys
                                                fresh_code_input.send_keys(Keys.RETURN)
                                                print("✅ 已按回车键提交")
                                            except Exception as key_e:
                                                print(f"❌ 按回车键失败: {key_e}")
                                        
                                        # 等待登录结果
                                        print("⏳ 等待登录结果...")
                                        time.sleep(5)
                                        
                                        # 检查登录状态
                                        new_url = login_manager.driver.current_url
                                        print(f"📄 登录后URL: {new_url}")
                                        
                                        if "login" not in new_url and "passport" not in new_url:
                                            print("🎉 登录成功！")
                                            break
                                        else:
                                            print("❌ 登录可能失败，继续等待...")
                                            time.sleep(3)
                                    else:
                                        print(f"⚠️ 验证码长度不足: {len(final_code)}位")
                                except Exception as code_e:
                                    print(f"❌ 获取最终验证码失败: {code_e}")
                            else:
                                print("❌ 无法获取验证码输入框")
                    except Exception as inner_e:
                        print(f"验证码检测内部错误: {inner_e}")
                        time.sleep(2)
                
                time.sleep(2)
                
            except Exception as e:
                print(f"检测过程出错: {e}")
                time.sleep(2)
        else:
            print("⏰ 登录等待超时")
            return False
        
        # 6. 测试搜索功能
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
        
        # 保存结果
        if candidates:
            candidate_manager.save_candidates_to_file(candidates, "search_results.json")
            print(f"\n💾 职位信息已保存到 search_results.json")
        
        print("\n🎉 搜索测试完成！")
        return True
        
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
    print("🔍 智联招聘搜索功能测试（修复版）")
    print("=" * 50)
    print("此脚本使用经过验证的登录逻辑")
    print("=" * 50)
    
    success = test_search_with_fixed_login()
    
    if success:
        print("\n🎉 测试完全成功！")
    else:
        print("\n❌ 测试失败")
    
    print("\n✨ 测试结束")