# SnackHot · 零食行业 AI 热点雷达

> 参照 [AIHOT](https://aihot.news) 技术路径，24 小时自动扫描 30+ 零食行业信源，LLM 智能摘要、聚类热点、每日早报。
> 前端：React + Vite + TailwindCSS
> 爬虫：Python + GitHub Actions
> 后端：热铁盒 Node.js 云函数 + KV 数据库
> 托管：热铁盒网页托管

## 目录结构

```
frontend/          # React 前端（AIHOT 风格）
crawler/           # Python 爬虫 + LLM 处理（GitHub Actions 定时跑）
  ├── sources/     # 各信源抓取器（Foodaily/巨潮/东方财富...）
  └── services/     # 处理服务（去重/分类/打分/聚类/存储）
cloud-functions/   # 热铁盒 Node.js 云函数（即 API Endpoint）
.github/workflows/ # GitHub Actions 定时调度
```

## 快速开始

### 1. 爬虫本地测试
```bash
cd crawler
pip install -r requirements.txt
cp .env.example .env   # 填 DOUBAO_API_KEY
python main.py         # 爬一次（没配 API Key 时用规则兜底）
```

### 2. 前端本地开发
```bash
cd frontend
npm install
npm run dev            # 默认用 mock 数据，没配热铁盒也能看
# 配热铁盒 API 后：
# VITE_API_BASE=https://snack-hot.rth1.xyz npm run dev
npm run build
```

### 3. 部署
```bash
cd frontend
deno -Ar https://host.retiehe.com/cli init   # 首次
npm run deploy                               # 一键部署到热铁盒
```

### 4. GitHub Actions Secrets（必需）
| Secret | 说明 |
|--------|------|
| `DOUBAO_API_KEY` | 豆包 API Key（没配时用规则兜底，但效果差） |
| `DOUBAO_MODEL` | 豆包模型 endpoint |
| `RTH_INGEST_URL` | 热铁盒 ingest 云函数 URL |
| `RTH_API_KEY` | 热铁盒 API Key |

## 核心流程

```
GitHub Actions (每 2h)
    │
    ▼
crawler/main.py
    ├─ 1. 抓取 → sources/* → RawItem[]
    ├─ 2. 去重 → 标题相似度
    ├─ 3. LLM  → 豆包 → 摘要 + 1-100 打分 + 分类 + 精选决策
    ├─ 4. 聚类 → TF-IDF + 余弦相似度 → EventCluster[]
    ├─ 5. 评分 → 热度分 = f(信源数, 报道数, 时间衰减, 品牌权重)
    └─ 6. 推送 → POST 热铁盒 /api/v1/ingest → KV 存储
                                        │
                                        ▼
                              云函数 API（items/hot-topics/story/daily）
                                        │
                                        ▼
                              React 前端（热铁盒静态托管 + CDN）
```

## 零食行业分类体系

```
品类：坚果炒货 / 肉脯卤味 / 膨化食品 / 糖果巧克力 / 饼干糕点 / 果冻蜜饯 / 冲调饮品 / 乳制品 / 其他
品牌：三只松鼠 / 良品铺子 / 百草味 / 卫龙 / 盐津铺子 / 来伊份 / 洽洽 / 旺旺 / 奥利奥 / 其他
事件类型：新品发布 / 财报业绩 / 渠道变革 / 食品安全 / 跨界联名 / 供应链变动 / 营销动态 / 行业政策
```

## 云函数 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/items?mode=&category=&limit=` | 资讯列表 |
| GET | `/api/v1/hot-topics` | 热点榜 Top 10 |
| GET | `/api/v1/story/:id` | 事件详情（聚合同事件所有报道） |
| GET | `/api/v1/daily/latest` | 每日早报 |
| POST | `/api/v1/ingest` | 爬虫写入入口 |
