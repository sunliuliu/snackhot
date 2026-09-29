import httpx, json

API_KEY = "sk-GfUXnrDC18Ux6729X5hYmFdX1vRXAvgd"
BASE = "https://token.sensenova.cn/v1"

# 1. 列所有可用模型
r = httpx.get(f"{BASE}/models", headers={"Authorization": f"Bearer {API_KEY}"}, timeout=15)
print(f"Models list status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    models = data.get("data", [])
    print(f"共 {len(models)} 个模型可用：")
    for m in models:
        mid = m.get("id", "")
        own = m.get("owned_by", "")
        print(f"  - {mid}  (owned_by={own})")
else:
    print(f"Error: {r.text[:300]}")

print()
print("--- 试试几个候选模型的 chat completion ---")

# 常见 Flash-Lite 免费模型
candidates = [
    "nova-ptc-xl-v2",          # 商汤大模型主力
    "nova-ptc-xl-v2-lite",     # 轻量版
    "nova-ptc-s-v2",           # 小型
    "nova-ptc-2024",
    "SenseNova-Flash-Lite",
    "sensechat-xl",
    "nova-pro",
]

for model in candidates:
    try:
        r = httpx.post(
            f"{BASE}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": "你好，请用 10 个字介绍自己"}],
                "max_tokens": 50,
            },
            timeout=15,
        )
        if r.status_code == 200:
            d = r.json()
            reply = d["choices"][0]["message"]["content"]
            usage = d.get("usage", {})
            print(f"[OK] {model}")
            print(f"     回复: {reply[:60]}")
            print(f"     tokens: {usage}")
            print()
        else:
            err = r.text[:200]
            print(f"[FAIL] {model} -> HTTP {r.status_code}: {err}")
            print()
    except Exception as e:
        print(f"[ERR] {model} -> {e}")
        print()