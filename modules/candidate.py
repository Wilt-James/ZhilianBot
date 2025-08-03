"""
候选人搜索和信息获取模块
"""
import time
import json
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

from config import settings
from utils import log


class CandidateManager:
    """候选人管理类"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.BROWSER_TIMEOUT)
    
    def search_candidates(self, 
                         keyword: str = "",
                         location: str = "",
                         experience: str = "",
                         education: str = "",
                         salary_range: str = "",
                         company_type: str = "",
                         page_limit: int = 5) -> List[Dict]:
        """
        搜索候选人
        
        Args:
            keyword: 关键词（职位、技能等）
            location: 工作地点
            experience: 工作经验
            education: 学历要求
            salary_range: 薪资范围
            company_type: 公司类型
            page_limit: 搜索页数限制
            
        Returns:
            候选人列表
        """
        try:
            log.info(f"开始搜索候选人，关键词: {keyword}")
            
            # 构建搜索URL
            search_url = self._build_search_url(
                keyword=keyword,
                location=location,
                experience=experience,
                education=education,
                salary_range=salary_range,
                company_type=company_type
            )
            
            candidates = []
            
            for page in range(1, page_limit + 1):
                log.info(f"正在搜索第 {page} 页...")
                
                # 构建分页URL - 智联招聘的分页格式是 /p{页码}
                if page == 1:
                    # 第一页不需要添加p1
                    page_url = search_url
                else:
                    # 其他页面需要在路径中添加 /p{页码}
                    if '?' in search_url:
                        base_path, params = search_url.split('?', 1)
                        page_url = f"{base_path}/p{page}?{params}"
                    else:
                        page_url = f"{search_url}/p{page}"
                
                log.debug(f"访问URL: {page_url}")
                self.driver.get(page_url)
                time.sleep(settings.REQUEST_DELAY)
                
                # 解析当前页面的候选人
                page_candidates = self._parse_candidate_list()
                if not page_candidates:
                    log.info("没有更多候选人，停止搜索")
                    break
                
                candidates.extend(page_candidates)
                log.info(f"第 {page} 页找到 {len(page_candidates)} 个候选人")
                
                # 避免请求过快
                time.sleep(settings.REQUEST_DELAY)
            
            log.info(f"搜索完成，共找到 {len(candidates)} 个候选人")
            return candidates
            
        except Exception as e:
            log.error(f"搜索候选人失败: {e}")
            return []
    
    def _build_search_url(self, **kwargs) -> str:
        """构建搜索URL - 基于智联招聘实际URL格式"""
        try:
            # 智联招聘的搜索URL格式: https://www.zhaopin.com/sou/jl{地区代码}/kw{关键词编码}/p{页码}
            base_url = settings.ZHILIAN_SEARCH_URL
            
            # 地区代码映射（部分常用城市）
            location_codes = {
                '北京': '530',
                '上海': '538', 
                '广州': '763',
                '深圳': '765',
                '杭州': '653',
                '南京': '635',
                '武汉': '736',
                '成都': '801',
                '西安': '854',
                '重庆': '551',
                '天津': '531',
                '苏州': '636',
                '郑州': '719',
                '长沙': '749',
                '东莞': '780',
                '青岛': '702',
                '沈阳': '565',
                '宁波': '681',
                '昆明': '831'
            }
            
            # 构建URL路径
            url_parts = []
            
            # 添加地区代码
            location = kwargs.get('location', '')
            if location:
                location_code = location_codes.get(location, '489')  # 默认使用489（全国）
                url_parts.append(f"jl{location_code}")
            
            # 添加关键词（智联招聘使用特殊编码）
            keyword = kwargs.get('keyword', '')
            if keyword:
                # 智联招聘关键词编码映射
                keyword_codes = {
                    'Java开发': '01500O80EO062NO0AF8G',
                    'java开发': '01500O80EO062NO0AF8G', 
                    'Java': '01500O80EO062NO0AF8G',
                    'java': '01500O80EO062NO0AF8G',
                    'Java开发工程师': '01500O80EO062NO0AF8G',
                    'java开发工程师': '01500O80EO062NO0AF8G',
                    'Python开发': '01500O80EO062',
                    'python开发': '01500O80EO062',
                    'Python': '01500O80EO062',
                    'python': '01500O80EO062',
                    'Python开发工程师': '01500O80EO062',
                    'python开发工程师': '01500O80EO062',
                    '前端开发': '01500O80EO062NO0AF8',
                    '前端': '01500O80EO062NO0AF8',
                    '前端工程师': '01500O80EO062NO0AF8',
                    'JavaScript': '01500O80EO062NO0AF8',
                    'Vue': '01500O80EO062NO0AF8',
                    'React': '01500O80EO062NO0AF8',
                    '后端开发': '01500O80EO062NO0AF8G',
                    '后端': '01500O80EO062NO0AF8G',
                    '后端工程师': '01500O80EO062NO0AF8G',
                    '全栈开发': '01500O80EO062',
                    '全栈': '01500O80EO062',
                    '软件开发': '01500O80EO062',
                    '软件工程师': '01500O80EO062',
                    'PHP开发': '01500O80EO062NO0AF8',
                    'PHP': '01500O80EO062NO0AF8',
                    'C++': '01500O80EO062NO0AF8',
                    'C#': '01500O80EO062NO0AF8',
                    '.NET': '01500O80EO062NO0AF8',
                    'Go开发': '01500O80EO062',
                    'Go': '01500O80EO062',
                    'Node.js': '01500O80EO062NO0AF8',
                    '数据库': '01500O80EO062NO0AF8',
                    'MySQL': '01500O80EO062NO0AF8',
                    'Redis': '01500O80EO062NO0AF8',
                    '运维': '01500O80EO062NO0AF8',
                    'DevOps': '01500O80EO062NO0AF8',
                    '测试': '01500O80EO062NO0AF8',
                    '测试工程师': '01500O80EO062NO0AF8',
                    '产品经理': '01500O80EO062NO0AF8',
                    'UI设计': '01500O80EO062NO0AF8',
                    'UE设计': '01500O80EO062NO0AF8'
                }
                
                # 查找关键词编码
                keyword_code = keyword_codes.get(keyword)
                if keyword_code:
                    url_parts.append(f"kw{keyword_code}")
                    log.debug(f"使用关键词编码: {keyword} -> {keyword_code}")
                else:
                    # 如果没有预定义编码，使用URL编码
                    import urllib.parse
                    encoded_keyword = urllib.parse.quote(keyword)
                    url_parts.append(f"kw{encoded_keyword}")
                    log.debug(f"使用URL编码: {keyword} -> {encoded_keyword}")
            
            # 构建完整URL
            if url_parts:
                search_path = "/".join(url_parts)
                search_url = f"{base_url}/{search_path}"
            else:
                search_url = f"{base_url}/jl489"  # 默认全国搜索
            
            # 添加其他参数
            params = []
            if kwargs.get('experience'):
                params.append(f"gx={kwargs['experience']}")
            if kwargs.get('education'):
                params.append(f"xl={kwargs['education']}")
            if kwargs.get('salary_range'):
                params.append(f"yx={kwargs['salary_range']}")
            if kwargs.get('company_type'):
                params.append(f"gm={kwargs['company_type']}")
            
            # 添加默认参数
            params.append("srccode=401801")  # 智联招聘的来源代码
            
            if params:
                search_url += f"?{'&'.join(params)}"
            
            log.debug(f"构建的搜索URL: {search_url}")
            return search_url
            
        except Exception as e:
            log.error(f"构建搜索URL失败: {e}")
            # 返回默认搜索URL
            return f"{settings.ZHILIAN_SEARCH_URL}/jl489?srccode=401801"
    
    def _parse_candidate_list(self) -> List[Dict]:
        """解析候选人列表页面 - 适配智联招聘实际页面结构"""
        try:
            candidates = []
            
            # 等待页面加载，尝试多种可能的选择器
            page_loaded = False
            selectors_to_try = [
                (By.CLASS_NAME, "joblist-box"),
                (By.CLASS_NAME, "positionlist"),
                (By.CLASS_NAME, "search-result"),
                (By.CSS_SELECTOR, ".search-result-list"),
                (By.CSS_SELECTOR, "[data-testid='job-list']"),
                (By.XPATH, "//div[contains(@class, 'job') or contains(@class, 'position')]")
            ]
            
            for selector_type, selector_value in selectors_to_try:
                try:
                    self.wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                    page_loaded = True
                    log.debug(f"页面加载成功，使用选择器: {selector_value}")
                    break
                except TimeoutException:
                    continue
            
            if not page_loaded:
                log.warning("页面加载超时，尝试直接解析")
            
            # 获取职位卡片，尝试多种选择器
            candidate_cards = []
            card_selectors = [
                ".jobinfo",
                ".position-item", 
                ".job-item",
                ".search-result-item",
                "[data-testid='job-item']",
                ".positionlist li",
                "div[class*='job']",
                "div[class*='position']"
            ]
            
            for selector in card_selectors:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards:
                        candidate_cards = cards
                        log.debug(f"找到 {len(cards)} 个职位卡片，使用选择器: {selector}")
                        break
                except:
                    continue
            
            if not candidate_cards:
                log.warning("未找到职位卡片，尝试通用解析")
                # 尝试通用方法
                candidate_cards = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'job') or contains(@class, 'position') or contains(text(), '万') or contains(text(), '千')]")
            
            log.info(f"找到 {len(candidate_cards)} 个职位卡片")
            
            # 限制处理的卡片数量，避免卡死
            max_cards = min(len(candidate_cards), 50)  # 最多处理50个
            
            for i, card in enumerate(candidate_cards[:max_cards]):
                try:
                    log.debug(f"正在解析第 {i+1}/{max_cards} 个职位...")
                    
                    # 添加超时机制 - Windows兼容版本
                    import threading
                    import time
                    
                    candidate_info = None
                    extraction_complete = threading.Event()
                    
                    def extract_with_timeout():
                        nonlocal candidate_info
                        try:
                            candidate_info = self._extract_candidate_basic_info(card)
                        except Exception as e:
                            log.debug(f"提取过程中出错: {e}")
                        finally:
                            extraction_complete.set()
                    
                    # 启动提取线程
                    extract_thread = threading.Thread(target=extract_with_timeout)
                    extract_thread.daemon = True
                    extract_thread.start()
                    
                    # 等待最多3秒
                    if extraction_complete.wait(timeout=3):
                        if candidate_info:
                            candidates.append(candidate_info)
                            log.info(f"✓ 成功解析第 {i+1} 个职位: {candidate_info.get('name', '未知')}")
                        else:
                            log.debug(f"第 {i+1} 个职位信息为空，跳过")
                    else:
                        log.warning(f"解析第 {i+1} 个职位信息超时，跳过")
                        continue
                        
                except TimeoutError:
                    log.warning(f"解析第 {i+1} 个职位信息超时，跳过")
                    continue
                except Exception as e:
                    log.warning(f"解析第 {i+1} 个职位信息失败: {e}")
                    continue
                
                # 每解析5个职位就输出一次进度
                if (i + 1) % 5 == 0:
                    log.info(f"已解析 {i+1}/{max_cards} 个职位，成功 {len(candidates)} 个")
            
            log.info(f"解析完成！总共处理 {max_cards} 个职位卡片，成功解析 {len(candidates)} 个职位信息")
            return candidates
            
        except Exception as e:
            log.error(f"解析候选人列表失败: {e}")
            return []
    
    def _extract_candidate_basic_info(self, card_element) -> Optional[Dict]:
        """从职位卡片提取基本信息 - 简化版本，避免卡死"""
        try:
            candidate = {}
            
            # 获取卡片的所有文本内容，用于快速解析
            try:
                card_text = card_element.text.strip()
                if not card_text:
                    return None
            except:
                return None
            
            # 职位名称和链接 - 简化查找
            try:
                # 优先查找链接
                link_element = None
                try:
                    link_element = card_element.find_element(By.TAG_NAME, "a")
                except:
                    pass
                
                if link_element:
                    candidate['name'] = link_element.text.strip()
                    candidate['profile_url'] = link_element.get_attribute("href") or ""
                else:
                    # 从文本中提取第一行作为职位名称
                    lines = card_text.split('\n')
                    candidate['name'] = lines[0].strip() if lines else "未知职位"
                    candidate['profile_url'] = ""
                    
            except Exception as e:
                log.debug(f"提取职位名称失败: {e}")
                candidate['name'] = "未知职位"
                candidate['profile_url'] = ""
            
            # 使用正则表达式从文本中快速提取信息
            import re
            
            # 薪资信息 - 从文本中提取
            try:
                salary_pattern = r'(\d+(?:\.\d+)?[-~]\d+(?:\.\d+)?[万千KkW元]|面议|薪资面议)'
                salary_match = re.search(salary_pattern, card_text)
                candidate['salary'] = salary_match.group(1) if salary_match else "面议"
            except:
                candidate['salary'] = "面议"
            
            # 工作地点 - 从文本中提取
            try:
                # 常见城市模式
                location_pattern = r'(北京|上海|广州|深圳|杭州|南京|武汉|成都|西安|重庆|天津|苏州|郑州|长沙|东莞|青岛|沈阳|宁波|昆明|大连|厦门|福州|石家庄|哈尔滨|济南|合肥|南昌|太原|兰州|银川|西宁|乌鲁木齐|拉萨|呼和浩特|南宁|海口|贵阳|长春|沈阳)(?:·[^·\s]+)*'
                location_match = re.search(location_pattern, card_text)
                candidate['location'] = location_match.group(0) if location_match else "未知地点"
            except:
                candidate['location'] = "未知地点"
            
            # 工作经验 - 从文本中提取
            try:
                exp_pattern = r'(\d+[-~]\d+年|\d+年以上|不限|应届|经验不限)'
                exp_match = re.search(exp_pattern, card_text)
                candidate['experience'] = exp_match.group(1) if exp_match else "经验不限"
            except:
                candidate['experience'] = "经验不限"
            
            # 学历要求 - 从文本中提取
            try:
                edu_pattern = r'(博士|硕士|本科|大专|专科|高中|中专|学历不限)'
                edu_match = re.search(edu_pattern, card_text)
                candidate['education'] = edu_match.group(1) if edu_match else "学历不限"
            except:
                candidate['education'] = "学历不限"
            
            # 公司信息 - 简化提取
            try:
                # 尝试快速查找公司名称
                lines = card_text.split('\n')
                candidate['company'] = "未知公司"
                for line in lines:
                    line = line.strip()
                    if line and not any(keyword in line for keyword in ['万', '千', '元', '年', '月', '日', '小时', '分钟']):
                        if len(line) > 2 and len(line) < 50:  # 公司名称长度合理
                            candidate['company'] = line
                            break
            except:
                candidate['company'] = "未知公司"
            
            # 发布时间 - 简化
            candidate['publish_time'] = "未知时间"
            
            # 验证是否提取到有效信息
            if candidate.get('name') and candidate['name'] != "未知职位":
                log.debug(f"成功提取职位信息: {candidate['name']} - {candidate['company']}")
                return candidate
            else:
                log.debug("未提取到有效职位信息")
                return None
            
        except Exception as e:
            log.error(f"提取职位基本信息失败: {e}")
            return None
    
    def get_candidate_detail(self, profile_url: str) -> Optional[Dict]:
        """获取候选人详细信息"""
        try:
            log.info(f"获取候选人详细信息: {profile_url}")
            
            # 检查URL是否有效
            if not profile_url or profile_url == "":
                log.warning("职位详情URL为空，跳过")
                return None
            
            # 访问候选人详情页
            try:
                self.driver.get(profile_url)
                time.sleep(settings.REQUEST_DELAY * 2)  # 增加等待时间
            except Exception as e:
                log.error(f"访问职位详情页失败: {e}")
                return None
            
            # 检查页面是否正常加载
            try:
                # 等待页面加载，尝试多种可能的元素
                page_loaded = False
                wait_selectors = [
                    (By.CLASS_NAME, "resume-info"),
                    (By.CLASS_NAME, "job-detail"),
                    (By.CLASS_NAME, "position-detail"),
                    (By.TAG_NAME, "body"),
                    (By.XPATH, "//div[contains(@class, 'detail') or contains(@class, 'info')]")
                ]
                
                for selector_type, selector_value in wait_selectors:
                    try:
                        self.wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                        page_loaded = True
                        log.debug(f"页面加载成功，检测到元素: {selector_value}")
                        break
                    except:
                        continue
                
                if not page_loaded:
                    log.warning("页面加载超时，尝试直接解析")
                
            except Exception as e:
                log.warning(f"等待页面加载失败: {e}")
            
            # 检查是否是有效的职位详情页
            current_url = self.driver.current_url
            page_title = ""
            try:
                page_title = self.driver.title
            except:
                pass
            
            # 如果页面重定向到登录页或错误页，返回基本信息
            if "login" in current_url.lower() or "error" in current_url.lower():
                log.warning("页面重定向到登录页或错误页，返回基本信息")
                return {
                    'name': '需要登录查看',
                    'url': profile_url,
                    'error': '页面需要登录或不可访问'
                }
            
            detail_info = {
                'url': profile_url,
                'title': page_title,
                'current_url': current_url
            }
            
            # 尝试从页面提取信息
            try:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                detail_info['page_content_length'] = len(page_text)
                
                # 如果页面内容太少，可能是加载失败
                if len(page_text) < 100:
                    log.warning("页面内容过少，可能加载失败")
                    detail_info['error'] = '页面内容加载不完整'
                    return detail_info
                
            except Exception as e:
                log.warning(f"获取页面内容失败: {e}")
                detail_info['error'] = '无法获取页面内容'
                return detail_info
            
            # 基本信息
            try:
                basic_info = self._extract_basic_info()
                detail_info.update(basic_info)
            except Exception as e:
                log.warning(f"提取基本信息失败: {e}")
            
            # 工作经历
            try:
                work_experience = self._extract_work_experience()
                detail_info['work_experience'] = work_experience
            except Exception as e:
                log.warning(f"提取工作经历失败: {e}")
                detail_info['work_experience'] = []
            
            # 教育经历
            try:
                education = self._extract_education()
                detail_info['education_history'] = education
            except Exception as e:
                log.warning(f"提取教育经历失败: {e}")
                detail_info['education_history'] = []
            
            # 技能标签
            try:
                skills = self._extract_skills()
                detail_info['skills'] = skills
            except Exception as e:
                log.warning(f"提取技能标签失败: {e}")
                detail_info['skills'] = []
            
            # 自我评价
            try:
                self_evaluation = self._extract_self_evaluation()
                detail_info['self_evaluation'] = self_evaluation
            except Exception as e:
                log.warning(f"提取自我评价失败: {e}")
                detail_info['self_evaluation'] = ""
            
            log.info(f"成功获取职位详细信息: {detail_info.get('name', '未知职位')}")
            return detail_info
            
        except Exception as e:
            log.error(f"获取候选人详细信息失败: {e}")
            # 返回基本错误信息而不是None
            return {
                'url': profile_url,
                'error': str(e),
                'name': '获取失败',
                'status': 'error'
            }
    
    def _extract_basic_info(self) -> Dict:
        """提取基本信息"""
        basic_info = {}
        
        try:
            # 姓名
            name_element = self.driver.find_element(By.CLASS_NAME, "resume-name")
            basic_info['name'] = name_element.text.strip()
        except:
            basic_info['name'] = "未知"
        
        try:
            # 年龄、性别等
            info_elements = self.driver.find_elements(By.CLASS_NAME, "resume-basic-info")
            for element in info_elements:
                text = element.text.strip()
                if "岁" in text:
                    basic_info['age'] = text
                elif text in ["男", "女"]:
                    basic_info['gender'] = text
                elif "年经验" in text:
                    basic_info['experience_years'] = text
        except:
            pass
        
        try:
            # 联系方式
            contact_element = self.driver.find_element(By.CLASS_NAME, "contact-info")
            basic_info['contact'] = contact_element.text.strip()
        except:
            basic_info['contact'] = ""
        
        return basic_info
    
    def _extract_work_experience(self) -> List[Dict]:
        """提取工作经历"""
        work_list = []
        
        try:
            work_sections = self.driver.find_elements(By.CLASS_NAME, "work-experience-item")
            
            for section in work_sections:
                work_item = {}
                
                try:
                    # 公司名称
                    company = section.find_element(By.CLASS_NAME, "company-name")
                    work_item['company'] = company.text.strip()
                except:
                    work_item['company'] = "未知"
                
                try:
                    # 职位
                    position = section.find_element(By.CLASS_NAME, "position-name")
                    work_item['position'] = position.text.strip()
                except:
                    work_item['position'] = "未知"
                
                try:
                    # 工作时间
                    duration = section.find_element(By.CLASS_NAME, "work-duration")
                    work_item['duration'] = duration.text.strip()
                except:
                    work_item['duration'] = "未知"
                
                try:
                    # 工作描述
                    description = section.find_element(By.CLASS_NAME, "work-description")
                    work_item['description'] = description.text.strip()
                except:
                    work_item['description'] = ""
                
                work_list.append(work_item)
        
        except:
            pass
        
        return work_list
    
    def _extract_education(self) -> List[Dict]:
        """提取教育经历"""
        education_list = []
        
        try:
            edu_sections = self.driver.find_elements(By.CLASS_NAME, "education-item")
            
            for section in edu_sections:
                edu_item = {}
                
                try:
                    # 学校名称
                    school = section.find_element(By.CLASS_NAME, "school-name")
                    edu_item['school'] = school.text.strip()
                except:
                    edu_item['school'] = "未知"
                
                try:
                    # 专业
                    major = section.find_element(By.CLASS_NAME, "major-name")
                    edu_item['major'] = major.text.strip()
                except:
                    edu_item['major'] = "未知"
                
                try:
                    # 学历
                    degree = section.find_element(By.CLASS_NAME, "degree")
                    edu_item['degree'] = degree.text.strip()
                except:
                    edu_item['degree'] = "未知"
                
                try:
                    # 时间
                    duration = section.find_element(By.CLASS_NAME, "edu-duration")
                    edu_item['duration'] = duration.text.strip()
                except:
                    edu_item['duration'] = "未知"
                
                education_list.append(edu_item)
        
        except:
            pass
        
        return education_list
    
    def _extract_skills(self) -> List[str]:
        """提取技能标签"""
        skills = []
        
        try:
            skill_elements = self.driver.find_elements(By.CLASS_NAME, "skill-tag")
            skills = [skill.text.strip() for skill in skill_elements if skill.text.strip()]
        except:
            pass
        
        return skills
    
    def _extract_self_evaluation(self) -> str:
        """提取自我评价"""
        try:
            evaluation_element = self.driver.find_element(By.CLASS_NAME, "self-evaluation")
            return evaluation_element.text.strip()
        except:
            return ""
    
    def save_candidates_to_file(self, candidates: List[Dict], filename: str = "candidates.json"):
        """保存候选人信息到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(candidates, f, ensure_ascii=False, indent=2)
            log.info(f"候选人信息已保存到 {filename}")
        except Exception as e:
            log.error(f"保存候选人信息失败: {e}")
    
    def load_candidates_from_file(self, filename: str = "candidates.json") -> List[Dict]:
        """从文件加载候选人信息"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                candidates = json.load(f)
            log.info(f"从 {filename} 加载了 {len(candidates)} 个候选人信息")
            return candidates
        except Exception as e:
            log.error(f"加载候选人信息失败: {e}")
            return []