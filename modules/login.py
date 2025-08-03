"""
智联招聘自动登录模块
"""
import time
import qrcode
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import base64

from config import settings
from utils import log


class ZhilianLogin:
    """智联招聘登录类"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self._setup_driver()
    
    def _setup_driver(self):
        """设置浏览器驱动"""
        try:
            chrome_options = Options()
            
            if settings.HEADLESS:
                chrome_options.add_argument("--headless")
            
            # 添加常用选项
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 设置用户代理
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 执行脚本隐藏webdriver特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.implicitly_wait(settings.IMPLICIT_WAIT)
            self.wait = WebDriverWait(self.driver, settings.BROWSER_TIMEOUT)
            
            log.info("浏览器驱动初始化成功")
            
        except Exception as e:
            log.error(f"浏览器驱动初始化失败: {e}")
            raise
    
    def login_with_sms(self, phone_number: str = None) -> bool:
        """使用手机验证码登录"""
        try:
            # 优先使用ZHILIAN_USERNAME，如果没有则使用USERNAME
            phone_number = phone_number or settings.ZHILIAN_USERNAME or settings.USERNAME
            
            if not phone_number:
                log.error("手机号未配置")
                return False
            
            log.info("开始手机验证码登录...")
            
            # 访问登录页面
            self.driver.get(settings.ZHILIAN_LOGIN_URL)
            time.sleep(2)
            
            # 输入手机号
            try:
                phone_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请输入手机号' or @placeholder='手机号' or contains(@class, 'phone')]"))
                )
                phone_input.clear()
                phone_input.send_keys(phone_number)
                log.info(f"已输入手机号: {phone_number}")
            except Exception as e:
                log.error(f"输入手机号失败: {e}")
                return False
            
            # 勾选用户协议 - 增强稳定性
            try:
                # 等待页面稳定
                time.sleep(2)
                
                # 查找并勾选用户协议复选框
                agreement_selectors = [
                    "//input[@type='checkbox']",
                    "//span[contains(text(), '已阅读并同意')]/../input",
                    "//label[contains(text(), '已阅读并同意')]//input",
                    "//div[contains(text(), '已阅读并同意')]//input",
                    ".agreement-checkbox input",
                    ".protocol-checkbox input",
                    ".checkbox input",
                    "#agreement",
                    "#protocol"
                ]
                
                agreement_checked = False
                for selector in agreement_selectors:
                    try:
                        # 重新查找元素，避免stale element
                        if selector.startswith("//"):
                            checkbox = self.driver.find_element(By.XPATH, selector)
                        else:
                            checkbox = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                        if checkbox.is_displayed():
                            # 检查是否已经勾选
                            if not checkbox.is_selected():
                                # 使用JavaScript点击，更稳定
                                try:
                                    self.driver.execute_script("arguments[0].click();", checkbox)
                                    log.info("已勾选用户服务协议（JavaScript方式）")
                                except:
                                    # 如果JavaScript失败，尝试普通点击
                                    try:
                                        checkbox.click()
                                        log.info("已勾选用户服务协议（普通方式）")
                                    except:
                                        # 尝试点击父元素
                                        parent = checkbox.find_element(By.XPATH, "..")
                                        parent.click()
                                        log.info("已勾选用户服务协议（点击父元素）")
                                
                                agreement_checked = True
                                break
                            else:
                                log.info("用户服务协议已勾选")
                                agreement_checked = True
                                break
                    except Exception as inner_e:
                        log.debug(f"尝试选择器 {selector} 失败: {inner_e}")
                        continue
                
                if not agreement_checked:
                    log.warning("未找到用户协议复选框，继续执行...")
                
                time.sleep(1)
                
            except Exception as e:
                log.warning(f"勾选用户协议失败，继续执行: {e}")
            
            # 点击获取验证码按钮 - 重新查找元素避免stale element
            try:
                # 等待一下确保页面稳定
                time.sleep(1)
                
                # 重新查找获取验证码按钮，尝试多种选择器
                sms_button_selectors = [
                    "//button[contains(text(), '获取验证码')]",
                    "//button[contains(text(), '发送验证码')]",
                    "//button[contains(text(), '获取短信验证码')]",
                    "//a[contains(text(), '获取验证码')]",
                    "//span[contains(text(), '获取验证码')]/..",
                    ".get-code-btn",
                    ".send-code-btn",
                    "#getCodeBtn"
                ]
                
                sms_button = None
                for selector in sms_button_selectors:
                    try:
                        if selector.startswith("//"):
                            button = self.driver.find_element(By.XPATH, selector)
                        else:
                            button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                        if button.is_displayed() and button.is_enabled():
                            sms_button = button
                            break
                    except:
                        continue
                
                if sms_button:
                    # 使用JavaScript点击，避免元素被遮挡
                    try:
                        self.driver.execute_script("arguments[0].click();", sms_button)
                        log.info("已点击获取验证码按钮（JavaScript方式）")
                    except:
                        # 如果JavaScript点击失败，尝试普通点击
                        sms_button.click()
                        log.info("已点击获取验证码按钮（普通方式）")
                    
                    time.sleep(2)
                else:
                    # 可能验证码按钮已经被点击过，或者页面结构发生变化
                    log.warning("未找到获取验证码按钮，可能已经发送过验证码")
                    
                    # 检查是否已经有验证码输入框
                    try:
                        # 使用更全面的选择器查找验证码输入框
                        code_input_selectors = [
                            "//input[@placeholder='请输入验证码']",
                            "//input[@placeholder='验证码']",
                            "//input[contains(@class, 'code')]",
                            "//input[contains(@class, 'verify')]",
                            "//input[contains(@class, 'sms')]",
                            "//input[@maxlength='4' or @maxlength='6']",
                            "//input[@type='text'][contains(@name, 'code')]",
                            "//input[@type='text'][contains(@id, 'code')]",
                            "//input[@type='text'][contains(@id, 'verify')]",
                            "//input[@type='text'][contains(@name, 'verify')]"
                        ]
                        
                        code_input_found = False
                        for selector in code_input_selectors:
                            try:
                                code_input = self.driver.find_element(By.XPATH, selector)
                                if code_input.is_displayed():
                                    log.info(f"发现验证码输入框（选择器: {selector}），继续等待用户输入...")
                                    code_input_found = True
                                    break
                            except:
                                continue
                        
                        if not code_input_found:
                            # 尝试查找所有可见的文本输入框
                            all_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                            visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]
                            
                            log.info(f"找到 {len(visible_inputs)} 个可见的文本输入框")
                            
                            if len(visible_inputs) >= 2:
                                # 假设第二个输入框是验证码框
                                log.info("使用第二个输入框作为验证码框，继续等待用户输入...")
                                code_input_found = True
                            elif len(visible_inputs) == 1:
                                # 只有一个输入框，可能手机号框已隐藏
                                log.info("使用唯一输入框作为验证码框，继续等待用户输入...")
                                code_input_found = True
                            else:
                                # 尝试查找任何类型的输入框
                                all_inputs_any = self.driver.find_elements(By.TAG_NAME, "input")
                                visible_any = [inp for inp in all_inputs_any if inp.is_displayed() and inp.get_attribute("type") in ["text", "tel", "number"]]
                                
                                if visible_any:
                                    log.info(f"找到 {len(visible_any)} 个其他类型的输入框，使用最后一个")
                                    code_input_found = True
                        
                        if not code_input_found:
                            log.warning("未找到验证码输入框，但继续等待（可能页面还在加载）")
                            # 不立即返回False，给页面更多时间加载
                            
                    except Exception as e:
                        log.warning(f"查找验证码输入框时出错: {e}，继续等待")
                        # 不立即返回False，继续尝试
                    
            except Exception as e:
                log.error(f"点击获取验证码按钮失败: {e}")
                return False
            
            # 等待用户手动输入验证码
            log.info("请查看手机短信并输入验证码...")
            
            # 尝试自动检测验证码输入或等待用户手动输入
            return self._wait_for_sms_input()
            
        except Exception as e:
            log.error(f"手机验证码登录失败: {e}")
            return False
    
    def _wait_for_sms_input(self) -> bool:
        """等待用户输入短信验证码"""
        try:
            log.info("等待验证码输入...")
            log.info("程序将自动检测验证码输入并尝试登录...")
            
            # 方式1：自动检测验证码输入框变化
            timeout = 120  # 2分钟超时
            start_time = time.time()
            last_log_time = 0
            
            while time.time() - start_time < timeout:
                try:
                    current_time = time.time()
                    
                    # 每30秒输出一次等待信息
                    if current_time - last_log_time > 30:
                        remaining_time = int(timeout - (current_time - start_time))
                        log.info(f"等待验证码输入中... 剩余时间: {remaining_time}秒")
                        last_log_time = current_time
                    
                    # 首先检查是否已经登录成功
                    if self.check_login_status():
                        log.info("检测到已登录成功")
                        return True
                    
                    # 检查验证码输入框 - 尝试多种选择器
                    sms_input_selectors = [
                        "//input[@placeholder='请输入验证码']",
                        "//input[@placeholder='验证码']", 
                        "//input[contains(@class, 'code')]",
                        "//input[contains(@class, 'sms')]",
                        "//input[contains(@class, 'verify')]",
                        "//input[@type='text'][contains(@name, 'code')]",
                        "//input[@type='text'][contains(@id, 'code')]",
                        "//input[@type='text'][contains(@id, 'verify')]",
                        "//input[@maxlength='4' or @maxlength='6']",
                        # 根据位置查找：获取验证码按钮附近的输入框
                        "//button[contains(text(), '获取验证码')]/preceding-sibling::input",
                        "//button[contains(text(), '获取验证码')]/..//input[@type='text']",
                        "//button[contains(text(), '发送验证码')]/..//input[@type='text']",
                        # 通用输入框（在登录页面中）
                        "//form//input[@type='text'][position()=2]",  # 通常验证码是第二个输入框
                        "//div[contains(@class, 'login')]//input[@type='text'][last()]"  # 最后一个文本输入框
                    ]
                    
                    sms_input = None
                    found_selector = None
                    for selector in sms_input_selectors:
                        try:
                            input_elem = self.driver.find_element(By.XPATH, selector)
                            if input_elem.is_displayed():
                                sms_input = input_elem
                                found_selector = selector
                                log.info(f"🔍 在检测循环中找到验证码输入框: {selector}")
                                break
                        except:
                            continue
                    
                    if not sms_input:
                        # 如果找不到验证码输入框，可能页面结构发生变化
                        # 尝试查找所有可见的文本输入框
                        try:
                            all_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                            visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]
                            
                            if len(visible_inputs) >= 2:
                                # 假设验证码输入框是第二个（第一个通常是手机号）
                                sms_input = visible_inputs[1]
                                log.debug("使用第二个可见输入框作为验证码输入框")
                            elif len(visible_inputs) == 1:
                                # 只有一个输入框，可能手机号已经隐藏
                                sms_input = visible_inputs[0]
                                log.debug("使用唯一可见输入框作为验证码输入框")
                        except:
                            pass
                    
                    if not sms_input:
                        time.sleep(2)
                        continue
                    
                    # 如果验证码框有内容且长度合适（通常4-6位）
                    try:
                        sms_value = sms_input.get_attribute('value') or ''
                        log.info(f"🔍 当前验证码输入框内容: '{sms_value}' (长度: {len(sms_value)})")
                        
                        if sms_value and len(sms_value) >= 4:
                            log.info(f"✅ 检测到验证码已输入: '{sms_value}' ({len(sms_value)}位)，尝试登录...")
                            
                            # 等待一下确保用户输入完成
                            time.sleep(2)
                            
                            # 重新获取验证码输入框（避免stale element）
                            # 优先使用之前成功的选择器
                            fresh_sms_input = None
                            if found_selector:
                                try:
                                    input_elem = self.driver.find_element(By.XPATH, found_selector)
                                    if input_elem.is_displayed():
                                        fresh_sms_input = input_elem
                                        log.debug(f"使用之前成功的选择器重新找到验证码输入框: {found_selector}")
                                except:
                                    pass
                            
                            # 如果优先选择器失败，尝试所有选择器
                            if not fresh_sms_input:
                                for selector in sms_input_selectors:
                                    try:
                                        input_elem = self.driver.find_element(By.XPATH, selector)
                                        if input_elem.is_displayed():
                                            fresh_sms_input = input_elem
                                            log.debug(f"重新找到验证码输入框: {selector}")
                                            break
                                    except:
                                        continue
                            
                            # 如果重新获取失败，使用原来的输入框
                            if not fresh_sms_input:
                                fresh_sms_input = sms_input
                                log.debug("重新获取验证码输入框失败，使用原输入框")
                            
                            # 再次检查验证码（确保用户输入完成）
                            try:
                                final_code = fresh_sms_input.get_attribute('value') or ''
                                log.info(f"最终验证码长度: {len(final_code)}位")
                                
                                if len(final_code) >= 4:
                                    log.info("🎯 尝试提交登录...")
                                    
                                    # 查找并点击登录按钮
                                    login_button_selectors = [
                                        "//button[contains(text(), '登录')]",
                                        "//button[contains(text(), '立即登录')]",
                                        "//button[contains(text(), '确认登录')]",
                                        "//button[contains(text(), '提交')]",
                                        "//a[contains(text(), '登录')]",
                                        "//input[@type='submit']",
                                        "//button[@type='submit']",
                                        "//form//button[last()]"  # 表单中的最后一个按钮
                                    ]
                                    
                                    log.info("🔍 查找登录按钮...")
                                    login_clicked = False
                                    for i, selector in enumerate(login_button_selectors):
                                        try:
                                            login_btn = self.driver.find_element(By.XPATH, selector)
                                            if login_btn.is_displayed() and login_btn.is_enabled():
                                                log.info(f"🎯 找到登录按钮 {i+1}: {login_btn.text}")
                                                # 使用JavaScript点击，更稳定
                                                self.driver.execute_script("arguments[0].click();", login_btn)
                                                log.info(f"✅ 已点击登录按钮: {login_btn.text}")
                                                login_clicked = True
                                                break
                                            else:
                                                log.debug(f"❌ 按钮 {i+1} 不可用: displayed={login_btn.is_displayed()}, enabled={login_btn.is_enabled()}")
                                        except Exception as btn_e:
                                            log.debug(f"❌ 按钮选择器 {i+1} 失败: {btn_e}")
                                            continue
                                    
                                    if not login_clicked:
                                        log.warning("🔄 未找到登录按钮，尝试按回车键提交")
                                        try:
                                            from selenium.webdriver.common.keys import Keys
                                            fresh_sms_input.send_keys(Keys.RETURN)
                                            log.info("✅ 已按回车键提交")
                                        except Exception as key_e:
                                            log.warning(f"❌ 按回车键失败: {key_e}")
                                    
                                    # 等待登录完成
                                    log.info("⏳ 等待登录结果...")
                                    time.sleep(5)
                                    
                                    # 等待登录成功
                                    if self._wait_for_login_success(timeout=30):
                                        return True
                                    else:
                                        log.warning("登录提交后未成功，继续等待...")
                                        time.sleep(3)
                                else:
                                    log.warning(f"⚠️ 验证码长度不足: {len(final_code)}位")
                            except Exception as code_e:
                                log.warning(f"❌ 获取最终验证码失败: {code_e}")
                    except Exception as sms_e:
                        log.warning(f"验证码检测出错: {sms_e}")
                        time.sleep(2)
                    
                    # 检查是否已经登录成功（有些情况下验证码输入后自动登录）
                    current_url = self.driver.current_url
                    if "zhaopin.com" in current_url and "login" not in current_url and "passport" not in current_url:
                        log.info("检测到已自动登录成功")
                        return True
                    
                    time.sleep(2)
                    
                except:
                    time.sleep(1)
                    continue
            
            # 方式2：如果自动检测失败，提示用户手动操作
            log.warning("自动检测验证码输入超时，请手动完成登录")
            input("请在浏览器中手动输入验证码并点击登录，完成后按回车键继续...")
            
            # 最后检查登录状态
            return self._wait_for_login_success(timeout=10)
            
        except Exception as e:
            log.error(f"等待验证码输入失败: {e}")
            return False
    
    def login_with_qrcode(self) -> bool:
        """使用二维码登录"""
        try:
            log.info("开始二维码登录...")
            
            # 访问登录页面
            self.driver.get(settings.ZHILIAN_LOGIN_URL)
            time.sleep(2)
            
            # 切换到二维码登录
            try:
                qr_tab = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), '扫码登录')]"))
                )
                qr_tab.click()
                time.sleep(1)
            except:
                log.warning("未找到扫码登录选项卡")
            
            # 获取二维码
            qr_img = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "qr-code"))
            )
            
            # 保存二维码图片
            qr_img.screenshot("qrcode.png")
            log.info("二维码已保存为 qrcode.png，请使用智联招聘APP扫码登录")
            
            # 等待登录成功
            return self._wait_for_login_success(timeout=120)  # 二维码登录等待时间更长
            
        except Exception as e:
            log.error(f"二维码登录失败: {e}")
            return False
    
    def _wait_for_login_success(self, timeout: int = 30) -> bool:
        """等待登录成功"""
        try:
            log.info("等待登录成功...")
            
            # 等待页面跳转或出现用户信息
            start_time = time.time()
            while time.time() - start_time < timeout:
                current_url = self.driver.current_url
                
                # 检查是否跳转到主页或个人中心
                if "zhaopin.com" in current_url and "login" not in current_url:
                    log.info("登录成功！")
                    return True
                
                # 检查是否需要验证码
                try:
                    captcha = self.driver.find_element(By.CLASS_NAME, "captcha")
                    if captcha.is_displayed():
                        log.warning("需要输入验证码，请手动处理")
                        input("请手动输入验证码并按回车继续...")
                except:
                    pass
                
                time.sleep(1)
            
            log.error("登录超时")
            return False
            
        except Exception as e:
            log.error(f"等待登录成功时出错: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            # 访问需要登录的页面
            self.driver.get("https://i.zhaopin.com")
            time.sleep(2)
            
            # 检查是否重定向到登录页面
            current_url = self.driver.current_url
            if "login" in current_url:
                return False
            
            # 检查是否有用户信息
            try:
                user_info = self.driver.find_element(By.CLASS_NAME, "user-info")
                return user_info.is_displayed()
            except:
                return False
                
        except Exception as e:
            log.error(f"检查登录状态失败: {e}")
            return False
    
    def find_element_safely(self, selectors, element_type="元素"):
        """安全地查找元素，避免stale element问题"""
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    element = self.driver.find_element(By.XPATH, selector)
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                if element.is_displayed():
                    return element
            except:
                continue
        return None

    def get_verification_code_input_robust(self):
        """稳定获取验证码输入框"""
        selectors = [
            "//input[@placeholder='请输入验证码']",
            "//input[@placeholder='验证码']",
            "//input[contains(@class, 'code')]",
            "//input[contains(@class, 'verify')]",
            "//input[@maxlength='4' or @maxlength='6']",
            "//input[@type='text'][contains(@name, 'code')]",
            "//input[@type='text'][contains(@id, 'code')]",
            "//input[@type='text'][contains(@id, 'verify')]"
        ]
        
        element = self.find_element_safely(selectors, "验证码输入框")
        if element:
            return element
        
        # 备用方案：查找所有文本输入框
        try:
            all_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
            visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]
            
            if len(visible_inputs) >= 2:
                return visible_inputs[1]  # 第二个通常是验证码
            elif len(visible_inputs) == 1:
                return visible_inputs[0]
        except:
            pass
        
        return None

    def login_with_sms_robust(self) -> bool:
        """稳定的短信验证码登录（参考test_robust_login.py）"""
        try:
            log.info("开始稳定短信验证码登录...")
            
            # 访问登录页面
            self.driver.get("https://passport.zhaopin.com/login")
            time.sleep(3)
            log.info(f"📄 当前页面: {self.driver.title}")
            
            # 1. 输入手机号
            phone_selectors = [
                "//input[@placeholder='请输入手机号']",
                "//input[@placeholder='手机号']",
                "//input[contains(@class, 'phone')]",
                "//input[@type='tel']"
            ]
            
            phone_input = self.find_element_safely(phone_selectors, "手机号输入框")
            if phone_input:
                phone_input.clear()
                # 使用配置中的手机号
                phone_number = settings.ZHILIAN_USERNAME or settings.USERNAME
                if not phone_number:
                    log.error("❌ 未配置手机号，请在config.py中设置ZHILIAN_USERNAME")
                    return False
                phone_input.send_keys(phone_number)
                log.info(f"✅ 已输入手机号: {phone_number[:3]}****{phone_number[-4:]}")
            else:
                log.error("❌ 未找到手机号输入框")
                return False
            
            time.sleep(2)
            
            # 2. 勾选协议
            try:
                checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                for checkbox in checkboxes:
                    if not checkbox.is_selected():
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        log.info("✅ 已勾选协议")
                        break
            except:
                log.warning("⚠️ 勾选协议失败")
            
            time.sleep(2)
            
            # 3. 点击获取验证码
            sms_selectors = [
                "//button[contains(text(), '获取验证码')]",
                "//button[contains(text(), '发送验证码')]"
            ]
            
            sms_button = self.find_element_safely(sms_selectors, "获取验证码按钮")
            if sms_button:
                self.driver.execute_script("arguments[0].click();", sms_button)
                log.info("✅ 已点击获取验证码")
            else:
                log.warning("⚠️ 未找到获取验证码按钮，继续...")
            
            time.sleep(3)
            
            # 4. 等待验证码输入
            log.info("📱 请输入验证码，程序将自动检测...")
            
            start_time = time.time()
            max_wait = 120
            last_log = 0
            
            while time.time() - start_time < max_wait:
                try:
                    current_time = time.time()
                    
                    # 状态输出
                    if current_time - last_log > 30:
                        remaining = int(max_wait - (current_time - start_time))
                        log.info(f"⏳ 等待验证码输入... 剩余: {remaining}秒")
                        last_log = current_time
                    
                    # 检查是否已登录
                    current_url = self.driver.current_url
                    if "login" not in current_url and "passport" not in current_url:
                        log.info("🎉 检测到已登录成功！")
                        return True
                    
                    # 重新获取验证码输入框
                    code_input = self.get_verification_code_input_robust()
                    if not code_input:
                        time.sleep(2)
                        continue
                    
                    # 检查验证码
                    try:
                        code_value = code_input.get_attribute('value') or ''
                        if len(code_value) >= 4:
                            log.info(f"✅ 检测到验证码: {len(code_value)}位")
                            time.sleep(2)  # 等待输入完成
                            
                            # 重新获取输入框确认
                            fresh_input = self.get_verification_code_input_robust()
                            if fresh_input:
                                final_code = fresh_input.get_attribute('value') or ''
                                if len(final_code) >= 4:
                                    log.info("🎯 提交登录...")
                                    
                                    # 查找登录按钮
                                    login_selectors = [
                                        "//button[contains(text(), '登录')]",
                                        "//button[contains(text(), '立即登录')]",
                                        "//button[@type='submit']"
                                    ]
                                    
                                    login_btn = self.find_element_safely(login_selectors, "登录按钮")
                                    if login_btn:
                                        self.driver.execute_script("arguments[0].click();", login_btn)
                                        log.info("✅ 已点击登录按钮")
                                    else:
                                        log.info("🔄 按回车键提交")
                                        from selenium.webdriver.common.keys import Keys
                                        fresh_input.send_keys(Keys.RETURN)
                                    
                                    # 等待结果
                                    time.sleep(5)
                                    
                                    # 检查登录状态
                                    new_url = self.driver.current_url
                                    log.info(f"📄 登录后URL: {new_url}")
                                    
                                    if "login" not in new_url and "passport" not in new_url:
                                        log.info("🎉 登录成功！")
                                        return True
                                    else:
                                        log.warning("❌ 登录失败，继续等待...")
                                        time.sleep(3)
                    except Exception as e:
                        log.warning(f"验证码检查出错: {e}")
                        time.sleep(2)
                    
                    time.sleep(2)
                    
                except Exception as e:
                    log.warning(f"登录循环出错: {e}")
                    time.sleep(2)
            else:
                log.warning("⏰ 登录超时")
                return False
                
        except Exception as e:
            log.error(f"稳定登录失败: {e}")
            return False

    def auto_login(self) -> bool:
        """自动登录（根据配置选择登录方式）"""
        try:
            # 先检查是否已经登录
            if self.is_logged_in():
                log.info("已经登录，无需重复登录")
                return True
            
            if settings.LOGIN_TYPE == "sms":
                return self.login_with_sms_robust()  # 使用稳定版本
            elif settings.LOGIN_TYPE == "qrcode":
                return self.login_with_qrcode()
            elif settings.LOGIN_TYPE == "password":
                log.warning("密码登录已不被支持，尝试使用手机验证码登录")
                return self.login_with_sms_robust()  # 使用稳定版本
            else:
                log.error(f"不支持的登录方式: {settings.LOGIN_TYPE}")
                return False
                
        except Exception as e:
            log.error(f"自动登录失败: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            log.info("浏览器已关闭")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()