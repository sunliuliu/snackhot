"""测试 SenseNova 所有可用模型，按速度+质量排序"""
import httpx, json, time, sys

API_KEY = "sk-GfUXnrDC18Ux6729X5hYmFdX1vRXAvgd"
BASE = "https://token.sensenova.cn/v1"

# 先拉真实可用模型列表（之前已经是 9 个了）
r = httpx.get(f"{BASE}/models", headers={"Authorization": f"Bearer {API_KEY}"}, timeout=15)
models = [m["id"] for m in r.json().get("data", [])]
print(f"账户下 {len(models)} 个可用模型: {models}\n")

SYSTEM = "你是零食行业分析师，输出严格 JSON 数组，每个元素有 summary, category, brands, event_type, score, reason 字段。"
USER = """[0] 来源: Foodaily
标题: 费列罗联手 Netflix 推出 Wonka 限量巧克力糖果
正文: 费列罗集团宣布与 Netflix 达成联名合作，推出 Wonka 电影主题限量版巧克力系列，借影视 IP 拓展巧克力消费场景。"""

results = []
for model in models:
    try:
        t0 = time.time()
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": USER},
            ],
            "max_tokens": 300,
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }
        # kimi-k3 不支持 temperature != 1，特殊处理
        if "kimi" in model:
            payload["temperature"] = 0.7
        r = httpx.post(
            f"{BASE}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        dt = time.time() - t0
        if r.status_code != 200:
            print(f"[SKIP] {model} -> HTTP {r.status_code}")
            continue
        d = r.json()
        content = d["choices"][0]["message"]["content"]
        usage = d.get("usage", {})
        # 评估 JSON 质量
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "summary" in parsed:
                json_ok = True
                json_score = len(parsed.get("summary", "")) > 10 and parsed.get("score", 0) > 50
            elif isinstance(parsed, list) and len(parsed) > 0:
                json_ok = True
                json_score = True
            else:
                json_ok = False
                json_score = False
        except Exception:
            json_ok = False
            json_score = False
        results.append({
            "model": model,
            "time": round(dt, 1),
            "in_tok": usage.get("prompt_tokens"),
            "out_tok": usage.get("completion_tokens"),
            "json_ok": json_ok,
            "json_score": json_score,
            "reply_preview": content[:100].replace("\n", " "),
        })
        tag = "⭐" if (json_ok and json_score) else ("❗" if not json_ok else "⚠️")
        print(f"{tag} {model:30s}  {dt:>5.1f}s  json={'OK' if json_ok else 'FAIL':4s}  score={'OK' if json_score else 'FAIL':4s}")
    except Exception as e:
        print(f"[ERR] {model} -> {str(e)[:60]}")

print(f"\n{'='*60}")
print("排序（速度优先，JSON 质量合格的才进入榜单）：")
good = sorted([r for r in results if r["json_ok"] and r["json_score"]], key=lambda x: x["time"])
for i, r in enumerate(good, 1):
    print(f"  #{i}  {r['model']}  用时 {r['time']}s  out_tokens={r['out_tok']}")