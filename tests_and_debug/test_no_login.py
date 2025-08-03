#!/usr/bin/env python3
"""
跳过登录，直接测试搜索功能
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


def test_search_without_login():
    """不登录直接测试搜索功能"""
    print("🔍 测试智联招聘搜索功能（无需登录）...")
    
    driver = None
    try:
        # 设置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # 初始化浏览器
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        print("✅ 浏览器初始化成功")
        
        # 直接访问搜索页面
        search_url = "https://sou.zhaopin.com/jobs/searchresult.ashx?jl=%E5%8C%97%E4%BA%AC&kw=Java%E5%BC%80%E5%8F%91&sm=0&p=1"
        print(f"🌐 访问搜索页面: {search_url}")
        
        driver.get(search_url)
        time.sleep(5)
        
        print(f"📄 当前页面标题: {driver.title}")
        print(f"📄 当前页面URL: {driver.current_url}")
        
        # 检查是否需要登录
        if "login" in driver.current_url.lower() or "passport" in driver.current_url.lower():
            print("❌ 页面重定向到登录页，需要登录才能搜索")
            return
        
        # 查找职位列表
        print("🔍 查找职位列表...")
        
        # 尝试多种职位列表选择器
        job_selectors = [
            ".joblist-box .job-list-box",
            ".joblist .job-list",
            ".search-result .job-item",
            ".job-list-item",
            ".job-item",
            "[data-jobid]",
            ".job-info"
        ]
        
        jobs = []
        for selector in job_selectors:
            try:
                job_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_elements:
                    jobs = job_elements
                    print(f"✅ 使用选择器 '{selector}' 找到 {len(jobs)} 个职位")
                    break
            except Exception as e:
                print(f"选择器 '{selector}' 失败: {e}")
        
        if not jobs:
            print("❌ 未找到职位列表，尝试分析页面结构...")
            
            # 分析页面结构
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text
                print(f"页面内容长度: {len(page_text)} 字符")
                
                if "职位" in page_text or "工作" in page_text:
                    print("✅ 页面包含职位相关内容")
                    
                    # 查找所有可能的职位容器
                    divs = driver.find_elements(By.TAG_NAME, "div")
                    print(f"找到 {len(divs)} 个div元素")
                    
                    # 查找包含职位信息的div
                    job_divs = []
                    for div in divs[:50]:  # 只检查前50个
                        try:
                            div_text = div.text.strip()
                            if len(div_text) > 20 and ("Java" in div_text or "开发" in div_text):
                                job_divs.append(div)
                        except:
                            continue
                    
                    print(f"找到 {len(job_divs)} 个可能的职位div")
                    
                    # 显示前几个职位信息
                    for i, job_div in enumerate(job_divs[:5]):
                        try:
                            job_text = job_div.text.strip()[:200]  # 只显示前200字符
                            print(f"\n职位 {i+1}:")
                            print(f"   内容: {job_text}")
                        except:
                            print(f"   职位 {i+1}: 无法获取内容")
                else:
                    print("❌ 页面不包含职位相关内容")
                    
            except Exception as e:
                print(f"分析页面失败: {e}")
        else:
            # 解析职位信息
            print(f"\n📋 解析 {len(jobs)} 个职位:")
            
            for i, job in enumerate(jobs[:10]):  # 只显示前10个
                try:
                    job_text = job.text.strip()
                    print(f"\n职位 {i+1}:")
                    print(f"   内容: {job_text[:300]}...")  # 只显示前300字符
                    
                    # 尝试提取职位链接
                    try:
                        link = job.find_element(By.TAG_NAME, "a")
                        href = link.get_attribute("href")
                        print(f"   链接: {href}")
                    except:
                        print("   链接: 未找到")
                        
                except Exception as e:
                    print(f"   职位 {i+1}: 解析失败 - {e}")
        
        print("\n🎉 搜索测试完成！")
        
        input("\n按回车键关闭浏览器...")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            try:
                driver.quit()
                print("🔒 浏览器已关闭")
            except:
                pass


if __name__ == "__main__":
    print("🚀 智联招聘搜索功能测试（无需登录）")
    print("=" * 50)
    print("注意：此测试直接访问搜索页面，不进行登录")
    print("=" * 50)
    
    test_search_without_login()