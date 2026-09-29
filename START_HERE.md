# 🚀 3 步上线 SnackHot

## 第 1 步：申请豆包 API Key（5 分钟）

1. 打开 https://console.volcengine.com/ark
2. 注册/登录 → 右上角创建 API Key → 复制保存（**只显示一次！**）
3. 去"模型推理" → 创建推理接入点 → 选 `doubao-pro-32k`（或任意免费模型）→ 拿到模型 ID（格式：`ep-2025xxxxxxxxxx-xxxxx`）
4. 填进 `crawler/.env`（复制 `.env.example` 改名）：
   ```
   DOUBAO_API_KEY=你的key
   DOUBAO_MODEL=你的模型ID
   ```
5. 本地跑一次验证：
   ```bash
   cd crawler && python main.py
   ```
   输出应该显示 `[LLM] 处理 batch 1（X 条）...` 而不是"未配置 API Key"

## 第 2 步：注册热铁盒 + 部署（10 分钟）

1. 打开 https://host.retiehe.com → 注册/登录
2. **新建网站** → 域名填 `snackhot.rth1.xyz` → 确定
3. 右上角菜单 → **API 密钥** → 新密钥 → 复制保存
4. 本地 CLI 初始化（需要先装 Deno：https://deno.com/）：
   ```bash
   cd frontend
   deno -Ar https://host.retiehe.com/cli init
   # 向导让你填：API Key + 选刚才建的网站
   npm run deploy    # Vite build + 上传热铁盒
   ```
5. 打开热铁盒在线 VS Code → 把 `cloud-functions/` 下所有 `.node.js` 文件**拖进网站根目录** → 保存即部署
6. 在线 VS Code 里找到 `ingest.node.js` 文件 → 看它的 URL 是什么（一般是 `https://你的域名/ingest`）
7. 把这个 URL 和 API Key 填进 `crawler/.env`：
   ```
   RTH_INGEST_URL=https://snackhot.rth1.xyz/ingest
   RTH_API_KEY=你的密钥
   ```
8. 跑一次完整推送：
   ```bash
   cd crawler && python main.py
   ```
   输出应该显示 `[推送] 成功 -> https://...`

## 第 3 步：GitHub Actions 定时爬取（5 分钟）

1. 把整个项目推到 GitHub：
   ```bash
   git init && git add . && git commit -m "init SnackHot" && git push -u origin main
   ```
2. GitHub Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**，依次加 3 个：
   | Name | Value |
   |------|-------|
   | `DOUBAO_API_KEY` | 豆包 Key |
   | `RTH_INGEST_URL` | 热铁盒 ingest URL |
   | `RTH_API_KEY` | 热铁盒 API Key |
3. Repo → **Actions** → 选 "SnackHot Crawler & Deploy" → 点 **Run workflow** 手动跑一次
4. 等它 finish（约 2 分钟）→ 打开 snackhot.rth1.xyz → **看到真实数据！** 🎉

---

## 完成后的自动流程

```
每 2 小时 自动触发
    ↓
GitHub Actions（Ubuntu）
    ↓
爬取 37 个信源 → 去重 → LLM 摘要打分
    ↓
TF-IDF 聚类 → 热度指数归一化
    ↓
POST /ingest → 热铁盒 KV 数据库
    ↓
前端从热铁盒 API 拉数据 → 展示
```

## 已完成 ✅

- [x] 前端 5 页 React + Tailwind 精致设计系统
- [x] 爬虫 Python + 4 个信源 + 去重 + LLM 兜底
- [x] TF-IDF 热点聚类 + 热度指数归一化 (100-600)
- [x] 6 个热铁盒云函数
- [x] GitHub Actions workflow（每 2h 自动跑）
- [x] SOURCES.md 信源清单 37 个

## 待你手动做 ⏳

- [ ] 豆包 API Key 申请
- [ ] 热铁盒注册 + API Key
- [ ] GitHub Repo + 3 个 Secrets
- [ ] 本地跑一次验证全链路