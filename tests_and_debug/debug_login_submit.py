#!/usr/bin/env python3
"""
调试登录提交问题的专用脚本
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.login import ZhilianLogin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def debug_login_submit():
    """调试登录提交问题"""
    print("🔍 调试登录提交问题...")
    
    try:
        # 初始化
        login_manager = ZhilianLogin()
        driver = login_manager.driver
        print("✅ 浏览器初始化成功")
        
        # 访问登录页面
        driver.get("https://passport.zhaopin.com/login")
        time.sleep(3)
        print(f"📄 当前页面: {driver.title}")
        
        # 1. 输入手机号
        phone_selectors = [
            "//input[@placeholder='请输入手机号']",
            "//input[@placeholder='手机号']",
            "//input[contains(@class, 'phone')]",
            "//input[@type='tel']"
        ]
        
        phone_input = None
        for selector in phone_selectors:
            try:
                phone_input = driver.find_element(By.XPATH, selector)
                if phone_input.is_displayed():
                    break
            except:
                continue
        
        if phone_input:
            phone_input.clear()
            phone_input.send_keys("16621536193")
            print("✅ 已输入手机号")
        else:
            print("❌ 未找到手机号输入框")
            return
        
        time.sleep(2)
        
        # 2. 勾选协议
        try:
            checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            for checkbox in checkboxes:
                if not checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox)
                    print("✅ 已勾选协议")
                    break
        except:
            print("⚠️ 勾选协议失败")
        
        time.sleep(2)
        
        # 3. 点击获取验证码
        sms_selectors = [
            "//button[contains(text(), '获取验证码')]",
            "//button[contains(text(), '发送验证码')]"
        ]
        
        sms_button = None
        for selector in sms_selectors:
            try:
                sms_button = driver.find_element(By.XPATH, selector)
                if sms_button.is_displayed() and sms_button.is_enabled():
                    break
            except:
                continue
        
        if sms_button:
            driver.execute_script("arguments[0].click();", sms_button)
            print("✅ 已点击获取验证码")
        else:
            print("⚠️ 未找到获取验证码按钮")
        
        time.sleep(3)
        
        # 4. 等待验证码输入并详细调试
        print("\n📱 请输入验证码，程序将详细分析每个步骤...")
        
        code_input_selectors = [
            "//input[@placeholder='请输入验证码']",
            "//input[@placeholder='验证码']",
            "//input[contains(@class, 'code')]",
            "//input[contains(@class, 'verify')]",
            "//input[@maxlength='4' or @maxlength='6']",
            "//input[@type='text'][contains(@name, 'code')]"
        ]
        
        start_time = time.time()
        max_wait = 120
        
        while time.time() - start_time < max_wait:
            try:
                remaining = int(max_wait - (time.time() - start_time))
                if remaining % 10 == 0:  # 每10秒输出一次
                    print(f"⏳ 等待验证码... 剩余: {remaining}秒")
                
                # 查找验证码输入框
                code_input = None
                found_selector = None
                
                for i, selector in enumerate(code_input_selectors):
                    try:
                        input_elem = driver.find_element(By.XPATH, selector)
                        if input_elem.is_displayed():
                            code_input = input_elem
                            found_selector = selector
                            break
                    except:
                        continue
                
                if not code_input:
                    # 尝试查找所有文本输入框
                    all_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
                    visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]
                    
                    if len(visible_inputs) >= 2:
                        code_input = visible_inputs[1]
                        found_selector = "第二个文本输入框"
                    elif len(visible_inputs) == 1:
                        code_input = visible_inputs[0]
                        found_selector = "唯一文本输入框"
                
                if code_input:
                    try:
                        code_value = code_input.get_attribute('value') or ''
                        
                        if len(code_value) >= 4:
                            print(f"\n✅ 检测到验证码: '{code_value}' (长度: {len(code_value)}位)")
                            print(f"🔍 使用的选择器: {found_selector}")
                            
                            # 等待用户输入完成
                            time.sleep(2)
                            
                            # 再次确认验证码
                            final_code = code_input.get_attribute('value') or ''
                            print(f"🔍 最终验证码: '{final_code}' (长度: {len(final_code)}位)")
                            
                            if len(final_code) >= 4:
                                print("\n🎯 开始查找登录按钮...")
                                
                                # 详细分析页面上的所有按钮
                                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                                print(f"📊 页面上共有 {len(all_buttons)} 个按钮:")
                                
                                for i, btn in enumerate(all_buttons):
                                    try:
                                        btn_text = btn.text.strip()
                                        btn_type = btn.get_attribute("type")
                                        btn_class = btn.get_attribute("class")
                                        displayed = btn.is_displayed()
                                        enabled = btn.is_enabled()
                                        
                                        print(f"   按钮 {i+1}: 文本='{btn_text}', type='{btn_type}', class='{btn_class}', 可见={displayed}, 可用={enabled}")
                                        
                                        if displayed and enabled and ("登录" in btn_text or btn_text == "" or "login" in btn_class.lower()):
                                            print(f"🎯 尝试点击按钮 {i+1}: '{btn_text}'")
                                            driver.execute_script("arguments[0].click();", btn)
                                            print(f"✅ 已点击按钮: '{btn_text}'")
                                            
                                            # 等待结果
                                            time.sleep(5)
                                            
                                            # 检查登录状态
                                            new_url = driver.current_url
                                            print(f"📄 点击后URL: {new_url}")
                                            
                                            if "login" not in new_url and "passport" not in new_url:
                                                print("🎉 登录成功！")
                                                return True
                                            else:
                                                print("❌ 登录失败，继续尝试其他按钮...")
                                    except Exception as btn_e:
                                        print(f"   按钮 {i+1} 分析失败: {btn_e}")
                                
                                # 如果没有找到合适的按钮，尝试按回车
                                print("\n🔄 尝试按回车键提交...")
                                try:
                                    code_input.send_keys(Keys.RETURN)
                                    print("✅ 已按回车键")
                                    
                                    time.sleep(5)
                                    
                                    new_url = driver.current_url
                                    print(f"📄 按回车后URL: {new_url}")
                                    
                                    if "login" not in new_url and "passport" not in new_url:
                                        print("🎉 按回车登录成功！")
                                        return True
                                    else:
                                        print("❌ 按回车也失败")
                                except Exception as key_e:
                                    print(f"❌ 按回车失败: {key_e}")
                                
                                # 分析表单提交
                                print("\n🔍 分析表单结构...")
                                try:
                                    forms = driver.find_elements(By.TAG_NAME, "form")
                                    print(f"📊 页面上共有 {len(forms)} 个表单")
                                    
                                    for i, form in enumerate(forms):
                                        try:
                                            form_action = form.get_attribute("action")
                                            form_method = form.get_attribute("method")
                                            print(f"   表单 {i+1}: action='{form_action}', method='{form_method}'")
                                            
                                            # 尝试提交表单
                                            print(f"🎯 尝试提交表单 {i+1}")
                                            driver.execute_script("arguments[0].submit();", form)
                                            
                                            time.sleep(5)
                                            
                                            new_url = driver.current_url
                                            print(f"📄 提交表单后URL: {new_url}")
                                            
                                            if "login" not in new_url and "passport" not in new_url:
                                                print("🎉 表单提交登录成功！")
                                                return True
                                        except Exception as form_e:
                                            print(f"   表单 {i+1} 提交失败: {form_e}")
                                except Exception as forms_e:
                                    print(f"分析表单失败: {forms_e}")
                                
                                print("❌ 所有登录尝试都失败了")
                                break
                    except Exception as code_e:
                        print(f"验证码检查失败: {code_e}")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"循环出错: {e}")
                time.sleep(2)
        
        print("⏰ 调试超时")
        return False
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        input("\n按回车键关闭浏览器...")
        try:
            login_manager.close()
            print("🔒 浏览器已关闭")
        except:
            pass


if __name__ == "__main__":
    print("🔍 登录提交问题调试工具")
    print("=" * 50)
    print("此脚本将详细分析登录提交的每个步骤")
    print("=" * 50)
    
    debug_login_submit()