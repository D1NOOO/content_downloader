from flask import Flask, request, jsonify
import logging
import time
import importlib
from urllib.parse import urlparse
from config import DOMAIN_SCRIPT_MAPPING, DEFAULT_SCRIPT

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/get_article', methods=['GET'])
def get_article():
    # 直接截取 /get_article?url= 后面的所有内容作为 URL
    full_path = request.full_path
    if not full_path or 'url=' not in full_path:
        logger.warning('URL is required')
        return jsonify({'error': 'URL is required'}), 400
    
    from urllib.parse import unquote
    url = full_path.split('url=', 1)[1]
    url = unquote(url)
    logger.info(f'Processing URL: {url}')
    print(f'待处理的URL: {url}')  # 添加这行来打印URL

    # 根据域名确定使用哪个脚本
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    # 查找匹配的脚本
    script_name = None
    for domain_key, script in DOMAIN_SCRIPT_MAPPING.items():
        if domain.endswith('.' + domain_key) or domain == domain_key:
            script_name = script
            break
    
    # 如果没有匹配的域名，使用默认脚本
    if script_name is None:
        script_name = DEFAULT_SCRIPT
    
    # 动态导入对应的模块
    try:
        module = importlib.import_module(script_name)
        # 对于微信公众号，函数名称是get_weixin_article_content
        if script_name == 'wx':
            get_content_func = getattr(module, 'get_weixin_article_content')
        else:
            get_content_func = getattr(module, f'get_{script_name}_content')
    except (ImportError, AttributeError) as e:
        logger.error(f'无法导入模块或获取函数: {e}')
        return jsonify({'error': '无法处理该域名的内容'}), 500
    
    start_time = time.time()
    result = get_content_func(url)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f'Processing completed in {elapsed_time:.2f} seconds')
    if result:
        logger.info('Article content retrieved successfully')
        return jsonify(result)
    else:
        logger.error('Failed to get article content')
        return jsonify({'error': 'Failed to get article content'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)