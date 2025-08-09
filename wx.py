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


def get_weixin_article_content(url: str) -> Optional[Dict[str, str]]:
    """
    获取微信公众号文章的标题和内容
    
    Args:
        url (str): 微信公众号文章链接
        
    Returns:
        Optional[Dict[str, str]]: 包含标题和内容的字典，如果获取失败则返回None
    """
    start_time = time.time()
    logger.info(f"开始处理URL: {url}")
    
    # 初始化浏览器
    edge_options = EdgeOptions()
    # 移除 --headless 和 --remote-debugging-port=9222 选项以排除问题
    # edge_options.add_argument('--headless')
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument('--disable-dev-shm-usage')
    edge_options.add_argument('--disable-gpu')
    # edge_options.add_argument('--remote-debugging-port=9222')
    
    # 从配置文件中读取 msedgedriver 的路径
    from config import msedgedriver_path
    
    try:
        browser = webdriver.Edge(executable_path=msedgedriver_path, options=edge_options)
    except WebDriverException as e:
        logger.error(f"浏览器初始化失败: {e}")
        return None
    
    try:
        # 打开文章链接
        browser.get(url)
        
        # 等待页面加载完成，检测页面上的某个元素是否出现
        try:
            WebDriverWait(browser, PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            logger.info("页面加载完成")
        except TimeoutException:
            logger.warning("页面加载超时")
        
        # 获取页面源码并解析
        page_source = browser.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 微信公众号文章标题一般在h1标签下，class为rich_media_title
        title_tag = soup.find('h1', class_="rich_media_title")
        title = title_tag.get_text().strip() if title_tag else "未找到标题"
        
        # 微信公众号文章内容在rich_media_area_primary的div标签下
        content_div =soup.find('div', class_="rich_media_area_primary")
        
        if content_div:
            # 获取文章内容的文本，去除一些标签和空白
            content = content_div.get_text().strip()
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
    # 测试代码
    test_url = input("请输入微信公众号文章链接: ")
    result = get_weixin_article_content(test_url)
    if result:
        print(f"标题: {result['title']}")
        print(f"内容: {result['content']}")
    else:
        print("未能获取文章内容")