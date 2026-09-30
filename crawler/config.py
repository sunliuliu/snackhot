"""全局配置"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).parent

# ==================== 通用大模型（OpenAI 兼容格式） ====================
LLM_BASE_URL   = os.getenv("LLM_BASE_URL", "")
LLM_API_KEY    = os.getenv("LLM_API_KEY", "")
LLM_MODEL      = os.getenv("LLM_MODEL", "")
LLM_TEMP       = float(os.getenv("LLM_TEMP", "0.3"))
LLM_TIMEOUT    = int(os.getenv("LLM_TIMEOUT", "60"))
FALLBACK_MODELS = [m.strip() for m in os.getenv("FALLBACK_MODELS", "").split(",") if m.strip()]
FALLBACK_TO_RULE = os.getenv("FALLBACK_TO_RULE", "true").lower() == "true"

# ==================== 热铁盒推送 ====================
RTH_INGEST_URL = os.getenv("RTH_INGEST_URL", "")
RTH_API_KEY    = os.getenv("RTH_API_KEY", "")

# ==================== 爬取 HTTP 通用 ====================
REQUEST_TIMEOUT = 15
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36"
}
MAX_ITEMS_PER_SOURCE = 50

# ==================== LLM 处理 ====================
SUMMARY_MAX_WORDS = 120
SCORE_THRESHOLD   = 60
BATCH_SIZE        = 8
MAX_RETRIES       = 2

# ==================== 热点聚类 ====================
SIMILARITY_THRESHOLD = 0.35
MIN_SOURCES_FOR_HOT  = 1

# ==================== 缓存 ====================
CACHE_DIR = BASE_DIR / "_cache"
DATA_DIR  = BASE_DIR / "_data"

# ========================================================================
# ⚠️ 速率控制配置 —— 稳字当头，所有值都是【最小等待秒数】
#    不允许高频触发。宁可慢，不要被封。
# ========================================================================

# --- 全局 ---
GLOBAL_MIN_INTERVAL = 2.0     # 任意两个请求之间的最小间隔（秒）

# --- 每个 source 单独节奏 ---
# dict key = crawler.name, value = (最小间隔秒, 最大间隔秒, 单日最大请求数)
# 实际间隔 = random(最小, 最大)，模拟人类节奏，不机械
SOURCE_RATES = {
    # ---------- 静态媒体网站（httpx 直接爬，相对安全） ----------
    "Foodaily 每日食品":   (1.5, 3.0,  200),    # 6 个页面，一页 3s 足够
    "联商网":              (2.0, 4.0,  100),    # 1-2 个页面
    "中国糖果网":           (2.0, 4.0,  100),
    "36氪-食品餐饮":        (3.0, 6.0,   80),    # 商业媒体较敏感

    # ---------- 财经 API（巨潮有官方 API，必须节制） ----------
    "巨潮资讯":             (5.0, 8.0,   50),    # 巨潮 API 严格限频
    "东方财富":             (3.0, 5.0,   80),
    "新浪财经":             (3.0, 5.0,   80),

    # ---------- Playwright（真实浏览器，最慢最慎） ----------
    "weibo":               (3.0, 5.5,  120),    # 29 关键词，必须慢！
    "rsshub":              (2.0, 4.0,  200),    # 自建路由（可控）
    "FoodTalks":           (2.0, 4.0,  150),    # 3 个页面, 垂直媒体
    "中国食品新闻网":        (2.0, 4.0,  120),    # 4 个页面, 官网较慢
    "中国食品安全网":        (2.0, 4.0,  120),    # 5 个页面, 监管类
    "新华网食品":           (2.5, 5.0,  100),    # 官方门户, 要稳
    "中国食品报":           (2.0, 4.0,  120),    # 4 个页面
}
DEFAULT_RATE = (2.0, 4.0, 100)

# --- 失败熔断 ---
FAILURE_COOLDOWN = 30.0        # 连续失败 N 次后冷却秒数
FAILURE_THRESHOLD = 3          # 连续几次失败触发熔断

# --- 每日总上限（防止 Github Actions 定时跑多轮） ---
DAILY_TOTAL_LIMIT = 600        # 所有 source 请求加起来不超这个数