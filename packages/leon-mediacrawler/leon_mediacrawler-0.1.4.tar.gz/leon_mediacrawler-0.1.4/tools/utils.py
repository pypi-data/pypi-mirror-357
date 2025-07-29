# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：  
# 1. 不得用于任何商业用途。  
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。  
# 3. 不得进行大规模爬取或对平台造成运营干扰。  
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。   
# 5. 不得用于任何非法或不当的用途。
#   
# 详细许可条款请参阅项目根目录下的LICENSE文件。  
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。  


import argparse
import logging
import os

from .crawler_util import *
from .slider_util import *
from .time_util import *


def get_resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径，兼容开发环境和打包环境
    
    Args:
        relative_path: 相对于包根目录的路径，如 'libs/stealth.min.js'
    
    Returns:
        资源文件的绝对路径
    """
    try:
        # 在打包环境中使用 importlib.resources 获取资源文件
        try:
            # Python 3.9+
            from importlib.resources import files
            package_path = files('leon_mediacrawler')
            return str(package_path / relative_path)
        except ImportError:
            # Python 3.7-3.8 fallback
            import pkg_resources
            return pkg_resources.resource_filename('leon_mediacrawler', relative_path)
    except:
        # 在开发环境中使用相对路径
        return relative_path


def init_loging_config():
    level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)s %(levelname)s (%(filename)s:%(lineno)d) - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    _logger = logging.getLogger("MediaCrawler")
    _logger.setLevel(level)
    return _logger


logger = init_loging_config()

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
