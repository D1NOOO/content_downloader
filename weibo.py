from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.edge.options import Options as EdgeOptions
import time
import re
import logging
from typing import Optional, Dict

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置参数
PAGE_LOAD_TIMEOUT = 10
CONTENT_CLEANUP_PATTERN = re.compile(r'\s+')


def get_weibo_content(url: str) -> Optional[Dict[str, str]]:
    """
    获取微博文章的标题和内容
    
    Args:
        url (str): 微博文章链接
        
    Returns:
        Optional[Dict[str, str]]: 包含标题和内容的字典，如果获取失败则返回None
    """
    start_time = time.time()
    logger.info(f"开始处理URL: {url}")
    
    # 初始化浏览器
    edge_options = EdgeOptions()
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument('--disable-dev-shm-usage')
    edge_options.add_argument('--disable-gpu')
    
    # 从配置文件中读取 msedgedriver 的路径
    try:
        from config import msedgedriver_path
        browser = webdriver.Edge(executable_path=msedgedriver_path, options=edge_options)
    except ImportError:
        logger.error("未找到配置文件或 msedgedriver 路径配置")
        return None
    except WebDriverException as e:
        logger.error(f"浏览器初始化失败: {e}")
        return None
    
    try:
        # 打开文章链接
        browser.get(url)
        
        # 等待页面加载完成
        try:
            WebDriverWait(browser, PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            logger.info("页面加载完成")
        except TimeoutException:
            logger.warning("页面加载超时")
        
        # 再等待一小段时间确保JavaScript内容完全加载
        time.sleep(2)
        
        # 获取页面源码并解析
        page_source = browser.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 根据用户要求，标题格式为"某某在几点发布了一条微博"
        # 查找发布人信息
        publisher = "未知用户"
        publisher_elements = soup.find_all('div', class_=lambda x: x and x.startswith('head_main_'))
        for element in publisher_elements:
            span = element.find('span')
            if span and span.get('title'):
                publisher = span.get('title')
                break
        
        # 查找发布时间信息
        publish_time = "未知时间"
        time_elements = soup.find_all('a', class_=lambda x: x and x.startswith('head-info_time_'))
        for element in time_elements:
            if element.get_text().strip():
                publish_time = element.get_text().strip()
                break
        
        # 组合标题
        title = f"{publisher}在{publish_time}发布了一条微博"
        
        # 微博文章内容可能在class为Main_full_???的div标签下（模糊匹配）
        # 使用正则表达式查找匹配的元素
        content_div = None
        for div in soup.find_all('div'):
            classes = div.get('class', [])
            for cls in classes:
                if isinstance(cls, str) and cls.startswith('Feed_body_'):
                    content_div = div
                    break
            if content_div:
                break
        
        # 如果通过BeautifulSoup没有找到，尝试使用Selenium直接查找
        if not content_div:
            try:
                # 查找所有div元素，然后筛选class包含Main_full_的元素
                all_divs = browser.find_elements(By.TAG_NAME, 'div')
                for div in all_divs:
                    classes = div.get_attribute('class')
                    if classes and 'Main_full_' in classes:
                        content_div = div
                        break
            except Exception as e:
                logger.warning(f"使用Selenium查找内容区域时出错: {e}")
        
        if content_div:
            # 获取文章内容的文本
            if isinstance(content_div, webdriver.remote.webelement.WebElement):
                # 如果是Selenium元素
                content = content_div.text
            else:
                # 如果是BeautifulSoup元素
                content = content_div.get_text().strip()
            
            # 进一步清理内容，去除视频相关信息等
            # 移除视频相关文本
            video_patterns = [
                r'播放视频播放.*?分享这条博文',
                r'视频地址.*?正在小窗播放中',
                r'点击展开.*?分享这条博文',
                r'\d{2}:\d{2}\s*/\s*时长\s*\d{2}:\d{2}',
                r'\d+\.\d+万次观看.*?分享这条博文'
            ]
            
            for pattern in video_patterns:
                content = re.sub(pattern, '', content, flags=re.DOTALL)
            
            # 清理内容，去除多余的空白字符和换行符
            content = CONTENT_CLEANUP_PATTERN.sub(' ', content).strip()
            return {'title': title, 'content': content}
        else:
            logger.warning("未找到文章内容区域")
            return None
            
    except WebDriverException as e:
        logger.error(f"WebDriver错误: {e}")
        return None
    except Exception as e:
        logger.error(f"处理页面时发生错误: {e}")
        return None
    finally:
        try:
            browser.quit()
        except Exception as e:
            logger.error(f"关闭浏览器时发生错误: {e}")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"处理完成，总耗时: {elapsed_time:.2f} 秒")

if __name__ == "__main__":
    # 测试链接
    try:
        test_url = input("请输入微博文章链接: ")
        
        # 获取文章内容
        article_data = get_weibo_content(test_url)
        
        if article_data:
            print(f"文章标题: {article_data['title']}")
            print(f"文章内容: {article_data['content'][:500]}...")  # 只打印前500个字符
        else:
            print("未能获取文章内容")
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")