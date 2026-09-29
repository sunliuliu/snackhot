"""诊断其他模型实际输出"""
import httpx, json, time

API_KEY = "sk-GfUXnrDC18Ux6729X5hYmFdX1vRXAvgd"
BASE = "https://token.sensenova.cn/v1"

SYSTEM = "你是零食行业分析师。"
USER = """请严格输出 JSON，数组形式，有一个元素，包含 summary, category, brands, event_type, score, reason 字段。
输入: 标题=费列罗联手Netflix推Wonka限量糖果"""

candidates = [
    ("glm-5.2", {"temperature": 0.3}),
    ("sensenova-6.8-flash-lite", {"temperature": 0.3}),
    ("deepseek-flash", {"temperature": 0.3}),
    ("deepseek-v4-pro", {"temperature": 0.3}),
]

for model, extra in candidates:
    print(f"\n{'='*50}")
    print(f"模型: {model}")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER},
        ],
        "max_tokens": 400,
        **extra,
    }
    try:
        r = httpx.post(
            f"{BASE}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        print(f"status: {r.status_code}")
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            print(f"content (前400字):\n{content[:400]}")
            print(f"---")
            # 尝试 parse
            try:
                json.loads(content)
                print("✅ JSON parse OK")
            except Exception as e:
                print(f"❌ JSON parse FAIL: {e}")
                # 加 response_format 再试
                print("  -> 加上 response_format 再试...")
                payload2 = {**payload, "response_format": {"type": "json_object"}}
                r2 = httpx.post(
                    f"{BASE}/chat/completions",
                    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                    json=payload2, timeout=30,
                )
                if r2.status_code == 200:
                    c2 = r2.json()["choices"][0]["message"]["content"]
                    print(f"  status={r2.status_code}, content(前200): {c2[:200]}")
                    try:
                        json.loads(c2); print("  ✅ 这次 OK")
                    except: print("  ❌ 还是 FAIL")
                else:
                    print(f"  -> 带 response_format 也 HTTP {r2.status_code}: {r2.text[:150]}")
        else:
            print(f"body: {r.text[:300]}")
    except Exception as e:
        print(f"ERR: {e}")
    time.sleep(1)