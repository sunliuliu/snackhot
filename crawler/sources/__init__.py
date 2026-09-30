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
from .caixin import CaixinCrawler
from .jiemian import JiemianCrawler
from .china_com import ChinaComCrawler
from .spzs import SpzsCrawler
from .cnstock import CnstockCrawler
from .samr import SamrCrawler
from .spgykj import SpgykjCrawler
from .chinacoop import ChinacoopCrawler

try:
    from .weibo import WeiboCrawler
    HAS_WEIBO = True
except ImportError as e:
    HAS_WEIBO = False
    print(f"  [sources] weibo import failed: {e}")

# ============ 同步 HTTPX 爬虫 ============
ALL_CRAWLERS = [
    # 原有 11 个
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
    # 第一轮新增 3 个
    CfnewsCrawler(),
    CfsnCrawler(),
    XinhuaFoodCrawler(),
    # 第二轮新增 5 个 (消费/财经/B2B)
    CaixinCrawler(),
    JiemianCrawler(),
    ChinaComCrawler(),
    SpzsCrawler(),
    CnstockCrawler(),
    # 第三轮新增 3 个 (监管/科技/供销)
    SamrCrawler(),
    SpgykjCrawler(),
    ChinacoopCrawler(),
]

# ============ 异步 / Playwright 爬虫 ============
ASYNC_CRAWLERS = []
if HAS_WEIBO:
    ASYNC_CRAWLERS.append(WeiboCrawler())
