#!/usr/bin/env python3
"""
专门调试验证码检测问题的脚本
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.login import ZhilianLogin
from selenium.webdriver.common.by import By


def test_code_detection():
    """测试验证码检测问题"""
    print("🔍 调试验证码检测问题...")
    
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
        
        # 4. 详细分析验证码输入框
        print("\n🔍 分析页面上的所有输入框...")
        
        # 查找所有输入框
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"📊 页面上共有 {len(all_inputs)} 个输入框:")
        
        code_candidates = []
        for i, inp in enumerate(all_inputs):
            try:
                input_type = inp.get_attribute("type")
                placeholder = inp.get_attribute("placeholder")
                name = inp.get_attribute("name")
                id_attr = inp.get_attribute("id")
                class_attr = inp.get_attribute("class")
                maxlength = inp.get_attribute("maxlength")
                displayed = inp.is_displayed()
                
                print(f"   输入框 {i+1}: type='{input_type}', placeholder='{placeholder}', name='{name}', id='{id_attr}', class='{class_attr}', maxlength='{maxlength}', 可见={displayed}")
                
                # 判断是否可能是验证码输入框
                if displayed and (
                    "验证码" in (placeholder or "") or
                    "code" in (name or "").lower() or
                    "code" in (id_attr or "").lower() or
                    "verify" in (name or "").lower() or
                    "verify" in (id_attr or "").lower() or
                    maxlength in ["4", "6"]
                ):
                    code_candidates.append((i+1, inp))
                    print(f"   ⭐ 输入框 {i+1} 可能是验证码输入框")
                    
            except Exception as e:
                print(f"   输入框 {i+1}: 分析失败 - {e}")
        
        print(f"\n🎯 找到 {len(code_candidates)} 个可能的验证码输入框")
        
        if not code_candidates:
            print("❌ 没有找到验证码输入框候选")
            return
        
        # 5. 监控验证码输入
        print("\n📱 请在浏览器中输入验证码，程序将实时监控所有候选输入框...")
        
        start_time = time.time()
        max_wait = 120
        
        while time.time() - start_time < max_wait:
            try:
                remaining = int(max_wait - (time.time() - start_time))
                if remaining % 10 == 0:  # 每10秒输出一次
                    print(f"⏳ 监控中... 剩余: {remaining}秒")
                
                # 检查所有候选输入框
                for idx, (input_num, input_elem) in enumerate(code_candidates):
                    try:
                        value = input_elem.get_attribute('value') or ''
                        if value:
                            print(f"📝 输入框 {input_num} 有内容: '{value}' (长度: {len(value)})")
                            
                            if len(value) >= 4:
                                print(f"✅ 输入框 {input_num} 验证码长度足够: '{value}'")
                                
                                # 尝试提交
                                print("🎯 尝试查找并点击登录按钮...")
                                
                                login_selectors = [
                                    "//button[contains(text(), '登录')]",
                                    "//button[contains(text(), '立即登录')]",
                                    "//button[@type='submit']"
                                ]
                                
                                login_clicked = False
                                for selector in login_selectors:
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
                                    print("🔄 尝试按回车键提交")
                                    from selenium.webdriver.common.keys import Keys
                                    input_elem.send_keys(Keys.RETURN)
                                
                                # 等待结果
                                time.sleep(5)
                                
                                # 检查登录状态
                                new_url = driver.current_url
                                print(f"📄 提交后URL: {new_url}")
                                
                                if "login" not in new_url and "passport" not in new_url:
                                    print("🎉 登录成功！")
                                    return True
                                else:
                                    print("❌ 登录失败，继续监控...")
                    except Exception as e:
                        print(f"检查输入框 {input_num} 失败: {e}")
                        # 移除失效的输入框
                        code_candidates.pop(idx)
                        break
                
                time.sleep(2)
                
            except Exception as e:
                print(f"监控循环出错: {e}")
                time.sleep(2)
        
        print("⏰ 监控超时")
        return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
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
    print("🔍 验证码检测问题调试工具")
    print("=" * 50)
    print("此脚本将详细分析验证码输入框并实时监控输入")
    print("=" * 50)
    
    test_code_detection()