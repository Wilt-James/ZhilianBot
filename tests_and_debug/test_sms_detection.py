#!/usr/bin/env python3
"""
专门测试验证码输入检测的脚本
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import log


def test_sms_detection():
    """测试验证码输入检测"""
    print("📱 测试验证码输入检测功能...")
    
    driver = None
    try:
        # 设置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 初始化浏览器
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        print("✅ 浏览器初始化成功")
        
        # 访问登录页面
        driver.get("https://passport.zhaopin.com/login")
        time.sleep(3)
        
        print(f"📄 当前页面: {driver.title}")
        
        # 输入手机号
        print("📱 输入手机号...")
        try:
            phone_input = driver.find_element(By.XPATH, "//input[@placeholder='请输入手机号' or @placeholder='手机号']")
            phone_input.clear()
            phone_input.send_keys("16621536193")
            print("✅ 手机号输入成功")
        except Exception as e:
            print(f"❌ 手机号输入失败: {e}")
            return
        
        time.sleep(2)
        
        # 勾选协议
        print("📋 勾选用户协议...")
        try:
            checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            for checkbox in checkboxes:
                if not checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox)
                    print("✅ 已勾选协议")
                    break
        except Exception as e:
            print(f"勾选协议失败: {e}")
        
        time.sleep(2)
        
        # 点击获取验证码
        print("🔘 点击获取验证码...")
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "验证码" in button.text:
                    driver.execute_script("arguments[0].click();", button)
                    print(f"✅ 已点击: {button.text}")
                    break
        except Exception as e:
            print(f"点击获取验证码失败: {e}")
        
        time.sleep(3)
        
        # 开始监控验证码输入
        print("\n🔍 开始监控验证码输入...")
        print("请在浏览器中输入收到的验证码，程序将自动检测...")
        
        start_time = time.time()
        max_wait = 120  # 2分钟
        last_log = 0
        
        while time.time() - start_time < max_wait:
            try:
                current_time = time.time()
                
                # 每30秒输出一次状态
                if current_time - last_log > 30:
                    remaining = int(max_wait - (current_time - start_time))
                    print(f"⏳ 等待验证码输入... 剩余时间: {remaining}秒")
                    last_log = current_time
                
                # 查找验证码输入框
                code_input_selectors = [
                    "//input[@placeholder='请输入验证码']",
                    "//input[@placeholder='验证码']",
                    "//input[contains(@class, 'code')]",
                    "//input[contains(@class, 'verify')]",
                    "//input[@maxlength='4' or @maxlength='6']"
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
                        code_input = visible_inputs[1]  # 第二个输入框通常是验证码
                        print("🔍 使用第二个输入框作为验证码框")
                    elif len(visible_inputs) == 1:
                        code_input = visible_inputs[0]
                        print("🔍 使用唯一输入框作为验证码框")
                
                if code_input:
                    code_value = code_input.get_attribute('value') or ''
                    
                    if code_value:
                        print(f"📝 检测到输入: '{code_value}' (长度: {len(code_value)})")
                        
                        if len(code_value) >= 4:
                            print("✅ 验证码长度足够，查找登录按钮...")
                            
                            # 查找登录按钮
                            login_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '登录')]")
                            if not login_buttons:
                                login_buttons = driver.find_elements(By.XPATH, "//button[@type='submit']")
                            if not login_buttons:
                                login_buttons = driver.find_elements(By.TAG_NAME, "button")
                            
                            print(f"🔍 找到 {len(login_buttons)} 个可能的登录按钮:")
                            for i, btn in enumerate(login_buttons):
                                try:
                                    btn_text = btn.text.strip()
                                    enabled = btn.is_enabled()
                                    displayed = btn.is_displayed()
                                    print(f"   按钮 {i+1}: '{btn_text}' (enabled={enabled}, displayed={displayed})")
                                    
                                    if displayed and enabled and ("登录" in btn_text or btn_text == ""):
                                        print(f"🎯 尝试点击按钮: '{btn_text}'")
                                        driver.execute_script("arguments[0].click();", btn)
                                        print("✅ 已点击登录按钮")
                                        
                                        # 等待页面变化
                                        time.sleep(5)
                                        
                                        # 检查登录结果
                                        new_url = driver.current_url
                                        print(f"📄 登录后URL: {new_url}")
                                        
                                        if "login" not in new_url and "passport" not in new_url:
                                            print("🎉 登录成功！")
                                            return True
                                        else:
                                            print("❌ 登录可能失败，继续等待...")
                                        break
                                except Exception as btn_e:
                                    print(f"   按钮 {i+1} 点击失败: {btn_e}")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"监控过程出错: {e}")
                time.sleep(2)
        
        print("⏰ 等待超时")
        return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if driver:
            input("\n按回车键关闭浏览器...")
            try:
                driver.quit()
                print("🔒 浏览器已关闭")
            except:
                pass


if __name__ == "__main__":
    print("🧪 验证码输入检测测试")
    print("=" * 50)
    print("此脚本将帮助调试验证码输入检测功能")
    print("请按照提示操作，程序会显示详细的检测过程")
    print("=" * 50)
    
    test_sms_detection()