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

# weibo 三模式自动切换: httpx+cookie / playwright / skip
# 无论是否有 Playwright 或 cookie，都不会 raise ImportError
# 无配置时 fetch() 自动返回空数组 + 打印 skip 日志
try:
    from .weibo import WeiboCrawler
    HAS_WEIBO = True
except ImportError as e:
    HAS_WEIBO = False
    print(f"  [sources] weibo import failed: {e}")

# ============ 同步 HTTPX 爬虫 ============
ALL_CRAWLERS = [
    FoodailyCrawler(),      # Foodaily 6 个零食分类页（主力，~60 条）
    LinkshopCrawler(),      # 联商网（零售行业最权威，~10 条）
    CninfoCrawler(),        # 巨潮零食上市公司公告（工作日爆发，5-15 条）
    EastmoneyCrawler(),     # 东财食品饮料新闻（宽泛过滤）
    SinaFinanceCrawler(),   # 新浪财经（宽泛过滤）
    Candy001Crawler(),      # 中国糖果网（糖果巧克力垂直）
    Kr36Crawler(),          # 36氪 RSS
    ThepaperCrawler(),      # 澎湃新闻 食品饮料 + 消费 + 财经
    Food21Crawler(),        # 食品商务网 (RSSHub 桥接)
    CeCrawler(),            # 中国经济网 食品板块
    RSSHubCrawler(),        # RSSHub 多源聚合
]

# ============ 异步 / Playwright 爬虫 ============
ASYNC_CRAWLERS = []
if HAS_WEIBO:
    ASYNC_CRAWLERS.append(WeiboCrawler())
