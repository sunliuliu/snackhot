import httpx, json, time

API_KEY = "sk-GfUXnrDC18Ux6729X5hYmFdX1vRXAvgd"
BASE = "https://token.sensenova.cn/v1"

models = [
    "sensenova-6.8-flash-lite",   # Flash-Lite 免费
    "sensenova-u1-fast",           # fast 版
    "sensenova-u1.5-lite",
    "deepseek-flash",
    "deepseek-v4-flash",
    "deepseek-v4.1-flash",
    "glm-5.2",
    "kimi-k3",
]

system_prompt = "你是零食行业分析师，输出严格 JSON 数组，每个元素有 summary, category, brands, event_type, score, reason 字段。"
user_prompt = """
[0] 来源: Foodaily 每日食品
标题: 费列罗联手 Netflix 推出 Wonka 限量巧克力糖果
正文: 费列罗集团宣布与 Netflix 达成联名合作，推出 Wonka 电影主题限量版巧克力系列...
"""

for model in models:
    try:
        t0 = time.time()
        r = httpx.post(
            f"{BASE}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": 300,
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )
        dt = time.time() - t0
        if r.status_code == 200:
            d = r.json()
            reply = d["choices"][0]["message"]["content"]
            usage = d.get("usage", {})
            print(f"[OK] {model}")
            print(f"     time: {dt:.1f}s  tokens: in={usage.get('prompt_tokens')} out={usage.get('completion_tokens')}")
            print(f"     reply: {reply[:120]}")
        else:
            err = r.text[:150]
            print(f"[FAIL] {model} -> HTTP {r.status_code}: {err}")
        print()
    except Exception as e:
        print(f"[ERR] {model} -> {e}")
        print()