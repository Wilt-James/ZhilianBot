#!/usr/bin/env python3
"""
最稳定的登录测试脚本 - 专门处理stale element问题
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.login import ZhilianLogin
from modules.candidate import CandidateManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils import log


def find_element_safely(driver, selectors, element_type="元素"):
    """安全地查找元素，避免stale element问题"""
    for selector in selectors:
        try:
            if selector.startswith("//"):
                element = driver.find_element(By.XPATH, selector)
            else:
                element = driver.find_element(By.CSS_SELECTOR, selector)
            
            if element.is_displayed():
                return element
        except:
            continue
    return None


def get_verification_code_input(driver):
    """获取验证码输入框"""
    selectors = [
        "//input[@placeholder='请输入验证码']",
        "//input[@placeholder='验证码']",
        "//input[contains(@class, 'code')]",
        "//input[contains(@class, 'verify')]",
        "//input[@maxlength='4' or @maxlength='6']",
        "//input[@type='text'][contains(@name, 'code')]"
    ]
    
    element = find_element_safely(driver, selectors, "验证码输入框")
    if element:
        return element
    
    # 备用方案：查找所有文本输入框
    try:
        all_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]
        
        if len(visible_inputs) >= 2:
            return visible_inputs[1]  # 第二个通常是验证码
        elif len(visible_inputs) == 1:
            return visible_inputs[0]
    except:
        pass
    
    return None


def test_robust_login():
    """最稳定的登录测试"""
    print("🛡️ 稳定登录测试（防stale element）...")
    
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
        
        phone_input = find_element_safely(driver, phone_selectors, "手机号输入框")
        if phone_input:
            phone_input.clear()
            phone_input.send_keys("16621536193")
            print("✅ 已输入手机号")
        else:
            print("❌ 未找到手机号输入框")
            return False
        
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
        
        sms_button = find_element_safely(driver, sms_selectors, "获取验证码按钮")
        if sms_button:
            driver.execute_script("arguments[0].click();", sms_button)
            print("✅ 已点击获取验证码")
        else:
            print("⚠️ 未找到获取验证码按钮，继续...")
        
        time.sleep(3)
        
        # 4. 等待验证码输入
        print("\n📱 请输入验证码，程序将自动检测...")
        
        start_time = time.time()
        max_wait = 120
        last_log = 0
        
        while time.time() - start_time < max_wait:
            try:
                current_time = time.time()
                
                # 状态输出
                if current_time - last_log > 30:
                    remaining = int(max_wait - (current_time - start_time))
                    print(f"⏳ 等待中... 剩余: {remaining}秒")
                    last_log = current_time
                
                # 检查是否已登录
                current_url = driver.current_url
                if "login" not in current_url and "passport" not in current_url:
                    print("🎉 检测到已登录成功！")
                    break
                
                # 重新获取验证码输入框
                code_input = get_verification_code_input(driver)
                if not code_input:
                    time.sleep(2)
                    continue
                
                # 检查验证码
                try:
                    code_value = code_input.get_attribute('value') or ''
                    if len(code_value) >= 4:
                        print(f"✅ 检测到验证码: {len(code_value)}位")
                        time.sleep(2)  # 等待输入完成
                        
                        # 重新获取输入框确认
                        fresh_input = get_verification_code_input(driver)
                        if fresh_input:
                            final_code = fresh_input.get_attribute('value') or ''
                            if len(final_code) >= 4:
                                print("🎯 提交登录...")
                                
                                # 查找登录按钮
                                login_selectors = [
                                    "//button[contains(text(), '登录')]",
                                    "//button[contains(text(), '立即登录')]",
                                    "//button[@type='submit']"
                                ]
                                
                                login_btn = find_element_safely(driver, login_selectors, "登录按钮")
                                if login_btn:
                                    driver.execute_script("arguments[0].click();", login_btn)
                                    print("✅ 已点击登录按钮")
                                else:
                                    print("🔄 按回车键提交")
                                    fresh_input.send_keys(Keys.RETURN)
                                
                                # 等待结果
                                time.sleep(5)
                                
                                # 检查登录状态
                                new_url = driver.current_url
                                print(f"📄 登录后URL: {new_url}")
                                
                                if "login" not in new_url and "passport" not in new_url:
                                    print("🎉 登录成功！")
                                    break
                                else:
                                    print("❌ 登录失败，继续等待...")
                                    time.sleep(3)
                except Exception as e:
                    print(f"验证码检查出错: {e}")
                    time.sleep(2)
                
                time.sleep(2)
                
            except Exception as e:
                print(f"循环出错: {e}")
                time.sleep(2)
        else:
            print("⏰ 登录超时")
            return False
        
        # 5. 测试搜索
        print("\n🔍 开始搜索测试...")
        candidate_manager = CandidateManager(driver)
        
        search_params = {
            'keyword': 'Java开发',
            'location': '北京',
            'page_limit': 1
        }
        
        candidates = candidate_manager.search_candidates(**search_params)
        print(f"🎯 搜索完成，找到 {len(candidates)} 个职位")
        
        # 显示结果
        for i, candidate in enumerate(candidates[:5], 1):
            print(f"📋 职位 {i}: {candidate.get('name', '未知')} - {candidate.get('company', '未知')}")
        
        if candidates:
            candidate_manager.save_candidates_to_file(candidates, "robust_search_results.json")
            print("💾 结果已保存")
        
        print("🎉 测试完成！")
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
    print("🛡️ 最稳定的登录+搜索测试")
    print("=" * 50)
    print("专门处理stale element问题")
    print("=" * 50)
    
    success = test_robust_login()
    
    if success:
        print("\n🎉 测试完全成功！")
    else:
        print("\n❌ 测试失败")
    
    print("\n✨ 测试结束")