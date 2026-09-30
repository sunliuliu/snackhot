from .base import BaseCrawler
from .foodaily import FoodailyCrawler
from .cninfo import CninfoCrawler
from .eastmoney import EastmoneyCrawler, WIDE_FOOD_KW
from .kr36 import Kr36Crawler
from .sina import SinaFinanceCrawler
from .linkshop import LinkshopCrawler
from .candy001 import Candy001Crawler
from .domestic_media import ThepaperCrawler, Food21Crawler, CeCrawler
from .rsshub import RSSHubCrawler
from .cfnews import CfnewsCrawler
from .cfsn import CfsnCrawler
from .news_cn import XinhuaFoodCrawler

try:
    from .weibo import WeiboCrawler
    HAS_WEIBO = True
except ImportError as e:
    HAS_WEIBO = False
    print(f"  [sources] weibo import failed: {e}")

# ============ 同步 HTTPX 爬虫 ============
ALL_CRAWLERS = [
    # ---- 原有 11 个 ----
    FoodailyCrawler(),
    LinkshopCrawler(),
    CninfoCrawler(),
    EastmoneyCrawler(),
    SinaFinanceCrawler(),
    Candy001Crawler(),
    Kr36Crawler(),
    ThepaperCrawler(),
    Food21Crawler(),
    CeCrawler(),
    RSSHubCrawler(),
    # ---- 新增 3 个 ----
    CfnewsCrawler(),       # 中国食品新闻网 (中食协, 25条)
    CfsnCrawler(),          # 中国食品安全网 (监管/抽检, 25条)
    XinhuaFoodCrawler(),    # 新华网食品频道 (权威)
]

# ============ 异步 / Playwright 爬虫 ============
ASYNC_CRAWLERS = []
if HAS_WEIBO:
    ASYNC_CRAWLERS.append(WeiboCrawler())
