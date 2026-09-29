"""用 Cookie 测试微博搜索能不能爬"""
import httpx, re

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

COOKIE_STR = "_s_tentry=open.weibo.com; Apache=2232659429518.3267.1790663717369; SINAGLOBAL=2232659429518.3267.1790663717369; ULV=1790663717380:1:1:1:2232659429518.3267.1790663717369:; PC_TOKEN=927576b640; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWHpT3MFaTr-XqUj045CY3O5NHD95Qp1K.EeoecS05pWs4DqcjxBJ8EdJHXUG.LxKBLBonLBoqt; ALF=02_1793255820"

# 解析 cookie string 成 dict
cookies = {}
for item in COOKIE_STR.split(";"):
    if "=" in item:
        k, v = item.strip().split("=", 1)
        cookies[k] = v

queries = ["三只松鼠", "卫龙", "好想来", "零食行业"]

with httpx.Client(headers=UA, cookies=cookies, timeout=20, follow_redirects=True) as c:
    for q in queries:
        url = f"https://s.weibo.com/weibo?q={q}&typeall=1&suball=1"
        r = c.get(url)
        
        print(f"\n{'='*60}")
        print(f"搜索: {q}")
        print(f"  status={r.status_code}  len={len(r.text)}  final={str(r.url)[:50]}")
        
        if "passport" in str(r.url) or "login" in str(r.url).lower():
            print(f"  ❌ Cookie 失效，被重定向登录")
            continue
        
        # 提取微博卡片
        cards = re.findall(r'<div[^>]*class="card-wrap"[^>]*>', r.text)
        print(f"  ✅ 抓到 {len(cards)} 条微博卡片")
        
        # 提取转发/评论/点赞
        rt_cmt = re.findall(r'<a[^>]*action-data="[^"]*"[^>]*>(\d+|赞|转发|评论)</a>', r.text)
        
        # 用更粗的正则抓内容
        # 转发数
        rts = re.findall(r'<a[^>]*>(\d+)</a>', r.text)[:20]
        # 标题/正文
        texts = re.findall(r'<p[^>]*node-type="feed_list_content"[^>]*>(.*?)</p>', r.text, re.DOTALL)
        if not texts:
            texts = re.findall(r'<div[^>]*class="content"[^>]*>(.*?)</div>', r.text, re.DOTALL)
        
        for t in texts[:5]:
            clean = re.sub(r'<[^>]+>', '', t).strip()[:80]
            if clean and len(clean) > 10:
                print(f"    - {clean}")