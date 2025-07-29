# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：  
# 1. 不得用于任何商业用途。  
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。  
# 3. 不得进行大规模爬取或对平台造成运营干扰。  
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。   
# 5. 不得用于任何非法或不当的用途。
#   
# 详细许可条款请参阅项目根目录下的LICENSE文件。  
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。  


import asyncio
import sys
import os

import cmd_arg
import config
import db
from base.base_crawler import AbstractCrawler
from media_platform.bilibili import BilibiliCrawler
from media_platform.douyin import DouYinCrawler
from media_platform.kuaishou import KuaishouCrawler
from media_platform.tieba import TieBaCrawler
from media_platform.weibo import WeiboCrawler
from media_platform.xhs import XiaoHongShuCrawler
from media_platform.zhihu import ZhihuCrawler
from store.xhs.xhs_store_impl import XhsJsonStoreImplement
from tools import utils

class CrawlerFactory:
    CRAWLERS = {
        "xhs": XiaoHongShuCrawler,
        "dy": DouYinCrawler,
        "ks": KuaishouCrawler,
        "bili": BilibiliCrawler,
        "wb": WeiboCrawler,
        "tieba": TieBaCrawler,
        "zhihu": ZhihuCrawler
    }

    @staticmethod
    def create_crawler(platform: str) -> AbstractCrawler:
        crawler_class = CrawlerFactory.CRAWLERS.get(platform)
        if not crawler_class:
            raise ValueError("Invalid Media Platform Currently only supported xhs or dy or ks or bili ...")
        return crawler_class()


async def main():
    # parse cmd
    await cmd_arg.parse_cmd()

    # store = XhsJsonStoreImplement()
    # await store.convert_comments_to_conversations()  # 使用 await 调用异步方法
    
    # init db
    if config.SAVE_DATA_OPTION == "db":
        # 检查Supabase环境变量
        supabase_url = os.getenv('SEO_SUPABASE_URL')
        supabase_key = os.getenv('SEO_SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            utils.logger.error("""
            ==================== Supabase Configuration Error ====================
            When SAVE_DATA_OPTION is set to "db", Supabase environment variables are required.
            
            Please set the following environment variables:
            - SEO_SUPABASE_URL: Your Supabase project URL
            - SEO_SUPABASE_ANON_KEY: Your Supabase anonymous key
            
            You can find these values in your Supabase project dashboard:
            1. Go to https://supabase.com/dashboard
            2. Select your project
            3. Go to Settings > API
            4. Copy the URL and anon/public key
            
            Example:
            export SEO_SUPABASE_URL="https://your-project.supabase.co"
            export SEO_SUPABASE_ANON_KEY="your-anon-key"
            
            Alternatively, you can change SAVE_DATA_OPTION to "json" or "csv" in config/base_config.py
            =====================================================================
            """)
            sys.exit(1)
        
        await db.init_db()

    crawler = CrawlerFactory.create_crawler(platform=config.PLATFORM)
    try:
        await crawler.start()
    finally:
        # 确保无论任务是否完成或出现异常，stop方法都会被调用
        await crawler.stop()

    if config.SAVE_DATA_OPTION == "db":
        await db.close()
    

def cli_main():
    """Command line interface entry point"""
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit()


if __name__ == '__main__':
    cli_main()
