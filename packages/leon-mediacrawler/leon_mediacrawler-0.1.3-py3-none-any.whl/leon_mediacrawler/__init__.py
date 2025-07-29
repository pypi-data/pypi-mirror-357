"""


Leon MediaCrawler - A social media crawler project

Support platforms: Xiaohongshu, Weibo, Zhihu, Bilibili, Douyin, BaiduTieBa etc.
"""

__version__ = "0.1.3"
__author__ = "Bradleon"
__email__ = "bradleon91@gmail.com"

# Import main modules for easier access
try:
    from . import config
    from . import base
    from . import cache
    from . import cmd_arg
    from . import constant
    from . import media_platform
    from . import model
    from . import proxy
    from . import tools
    from . import store
    from . import utils
    
    # Import core modules
    from . import db
    from . import async_db
    from . import var
    
except ImportError:
    # Fallback for development mode
    import config
    import base
    import cache
    import cmd_arg
    import constant
    import media_platform
    import model
    import proxy
    import tools
    import store
    import utils
    import db
    import async_db
    import var

__all__ = [
    "config",
    "base", 
    "cache",
    "cmd_arg",
    "constant",
    "media_platform",
    "model",
    "proxy",
    "tools",
    "store",
    "utils",
    "db",
    "async_db", 
    "var",
    "__version__",
    "__author__",
    "__email__"
] 