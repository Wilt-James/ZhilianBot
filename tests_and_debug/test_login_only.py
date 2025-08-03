#!/usr/bin/env python3
"""
只测试登录功能的脚本
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.login import ZhilianLogin
from utils import log


def test_login_step_by_step():
    """分步测试登录功能"""
    print("🔐 分步测试智联招聘登录功能...")
    
    try:
        # 初始化登录管理器
        login_manager = ZhilianLogin()
        print("✅ 浏览器初始化成功")
        
        # 访问登录页面
        print("🌐 访问登录页面...")
        login_manager.driver.get("https://passport.zhaopin.com/login")
        time.sleep(3)
        
        print("📄 当前页面标题:", login_manager.driver.title)
        print("📄 当前页面URL:", login_manager.driver.current_url)
        
        # 手动输入手机号
        print("📱 输入手机号...")
        from selenium.webdriver.common.by import By
        
        try:
            phone_input = login_manager.driver.find_element(By.XPATH, "//input[@placeholder='请输入手机号' or @placeholder='手机号' or contains(@class, 'phone')]")
            phone_input.clear()
            phone_input.send_keys("16621536193")
            print("✅ 手机号输入成功")
        except Exception as e:
            print(f"❌ 手机号输入失败: {e}")
            
            # 尝试其他方法
            try:
                phone_input = login_manager.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
                phone_input.clear()
                phone_input.send_keys("16621536193")
                print("✅ 手机号输入成功（备用方法）")
            except Exception as e2:
                print(f"❌ 备用方法也失败: {e2}")
                return
        
        time.sleep(2)
        
        # 查找用户协议
        print("📋 查找用户协议...")
        try:
            checkboxes = login_manager.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            print(f"找到 {len(checkboxes)} 个复选框")
            
            for i, checkbox in enumerate(checkboxes):
                try:
                    if not checkbox.is_selected():
                        login_manager.driver.execute_script("arguments[0].click();", checkbox)
                        print(f"✅ 勾选了第 {i+1} 个复选框")
                        break
                except Exception as e:
                    print(f"勾选第 {i+1} 个复选框失败: {e}")
        except Exception as e:
            print(f"查找复选框失败: {e}")
        
        time.sleep(2)
        
        # 查找获取验证码按钮
        print("🔘 查找获取验证码按钮...")
        try:
            buttons = login_manager.driver.find_elements(By.TAG_NAME, "button")
            print(f"找到 {len(buttons)} 个按钮")
            
            for i, button in enumerate(buttons):
                try:
                    button_text = button.text.strip()
                    print(f"按钮 {i+1}: '{button_text}'")
                    
                    if "验证码" in button_text or "获取" in button_text:
                        if button.is_displayed() and button.is_enabled():
                            print(f"尝试点击按钮: {button_text}")
                            login_manager.driver.execute_script("arguments[0].click();", button)
                            print("✅ 成功点击获取验证码按钮")
                            break
                except Exception as e:
                    print(f"处理按钮 {i+1} 失败: {e}")
        except Exception as e:
            print(f"查找按钮失败: {e}")
        
        print("\n⏳ 请在浏览器中手动完成剩余步骤...")
        print("1. 检查是否收到短信验证码")
        print("2. 在页面中输入验证码")
        print("3. 点击登录按钮")
        
        input("\n按回车键关闭浏览器...")
        
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


def test_page_elements():
    """测试页面元素"""
    print("🔍 测试页面元素...")
    
    try:
        login_manager = ZhilianLogin()
        
        # 访问登录页面
        login_manager.driver.get("https://passport.zhaopin.com/login")
        time.sleep(3)
        
        print("📄 页面信息:")
        print(f"   标题: {login_manager.driver.title}")
        print(f"   URL: {login_manager.driver.current_url}")
        
        # 获取页面源码的一部分
        page_source = login_manager.driver.page_source
        print(f"   页面源码长度: {len(page_source)} 字符")
        
        # 查找所有输入框
        from selenium.webdriver.common.by import By
        
        inputs = login_manager.driver.find_elements(By.TAG_NAME, "input")
        print(f"\n📝 找到 {len(inputs)} 个输入框:")
        for i, inp in enumerate(inputs):
            try:
                input_type = inp.get_attribute("type")
                placeholder = inp.get_attribute("placeholder")
                name = inp.get_attribute("name")
                class_name = inp.get_attribute("class")
                print(f"   输入框 {i+1}: type='{input_type}', placeholder='{placeholder}', name='{name}', class='{class_name}'")
            except:
                print(f"   输入框 {i+1}: 无法获取属性")
        
        # 查找所有按钮
        buttons = login_manager.driver.find_elements(By.TAG_NAME, "button")
        print(f"\n🔘 找到 {len(buttons)} 个按钮:")
        for i, btn in enumerate(buttons):
            try:
                text = btn.text.strip()
                class_name = btn.get_attribute("class")
                enabled = btn.is_enabled()
                displayed = btn.is_displayed()
                print(f"   按钮 {i+1}: '{text}', class='{class_name}', enabled={enabled}, displayed={displayed}")
            except:
                print(f"   按钮 {i+1}: 无法获取属性")
        
        input("\n按回车键关闭浏览器...")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        try:
            login_manager.close()
        except:
            pass


if __name__ == "__main__":
    print("🧪 智联招聘登录调试工具")
    print("=" * 50)
    
    choice = input("选择测试模式:\n1. 分步登录测试\n2. 页面元素分析\n请输入 1 或 2: ").strip()
    
    if choice == "1":
        test_login_step_by_step()
    elif choice == "2":
        test_page_elements()
    else:
        print("无效选择")
    
    print("\n✨ 测试结束")