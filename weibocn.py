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


def get_weibocn_content(url: str) -> Optional[Dict[str, str]]:
    """
    获取手机端微博文章的标题和内容
    
    Args:
        url (str): 手机端微博文章链接
        
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
        
        # 查找发布人信息
        publisher = "未知用户"
        publisher_element = soup.find('h3', class_="m-text-cut")
        if publisher_element:
            publisher = publisher_element.get_text().strip()
        
        # 查找发布时间信息
        publish_time = "未知时间"
        time_element = soup.find('span', class_="time")
        if time_element:
            publish_time = time_element.get_text().strip()
        
        # 组合标题
        title = f"{publisher}在{publish_time}发布了一条微博"
        
        # 查找文章内容区域
        content_div = soup.find('div', class_="lite-page-wrap")
        
        if content_div:
            # 获取文章内容的文本
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
    # 测试链接
    try:
        test_url = input("请输入手机端微博文章链接: ")
        
        # 获取文章内容
        article_data = get_weibocn_content(test_url)
        
        if article_data:
            print(f"文章标题: {article_data['title']}")
            print(f"文章内容: {article_data['content']}")
        else:
            print("未能获取文章内容")
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")