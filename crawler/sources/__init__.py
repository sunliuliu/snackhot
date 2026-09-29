from .base import BaseCrawler
from .foodaily import FoodailyCrawler
from .cninfo import CninfoCrawler
from .eastmoney import EastmoneyCrawler, WIDE_FOOD_KW
from .kr36 import Kr36Crawler
from .sina import SinaFinanceCrawler
from .linkshop import LinkshopCrawler
from .candy001 import Candy001Crawler
from .domestic_media import ThepaperCrawler, Food21Crawler, CeCrawler

try:
    from .weibo import WeiboCrawler
    HAS_WEIBO = True
except ImportError:
    HAS_WEIBO = False

ALL_CRAWLERS = [
    FoodailyCrawler(),      # Foodaily 6 个零食分类页（主力，~60 条）
    LinkshopCrawler(),      # 联商网（零售行业最权威，~10 条）
    CninfoCrawler(),        # 巨潮零食上市公司公告（工作日爆发，5-15 条）
    EastmoneyCrawler(),     # 东财食品饮料新闻（宽泛过滤）
    SinaFinanceCrawler(),   # 新浪财经（宽泛过滤）
    Candy001Crawler(),      # 中国糖果网（糖果巧克力垂直）
    Kr36Crawler(),          # 36氪 RSS
    ThepaperCrawler(),      # 澎湃新闻 食品饮料
    Food21Crawler(),        # 食品商务网 行业资讯
    CeCrawler(),            # 中国经济网 食品板块
]

# Playwright 爬虫（异步，单独跑）
ASYNC_CRAWLERS = []
if HAS_WEIBO:
    ASYNC_CRAWLERS.append(WeiboCrawler())
