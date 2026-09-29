# 热铁盒云函数

本目录下的 `.node.js` 文件为 **Node.js 云函数**，上传到热铁盒网页托管后即可自动识别为 API Endpoint。

## 部署方式

### 方式 A：在线 VS Code 直接上传（最简单）
1. 打开热铁盒网页托管管理页
2. 打开你的网站（比如 snack-hot.rth1.xyz）
3. 打开在线 VS Code
4. 把 `.node.js` 文件拖进去，保存即部署

文件名即路由：
- `ingest.node.js` → `/ingest`
- `items.node.js` → `/items`
- `hot-topics.node.js` → `/hot-topics`
- `story.node.js` → `/story`
- `daily.node.js` → `/daily`

### 方式 B：CLI 一键部署
```bash
cd <项目根目录>
deno -Ar https://host.retiehe.com/cli init  # 首次初始化
npm run deploy                               # 后续一键部署
```

## KV 数据库键设计

| Key | 类型 | 说明 |
|-----|------|------|
| `item:{id}` | JSON | 单条 ProcessedItem |
| `event:{id}` | JSON | 单个 EventCluster |
| `index:selected` | JSON Array | 精选 item id 列表（最多 200） |
| `index:events` | JSON Array | event id 列表（按 hot_score 排序） |
| `daily:YYYY-MM-DD` | JSON | 当日日报 |
| `daily:latest` | String | 最新日报的 key |

## 内置对象（热铁盒 Node.js 云函数）

- `Database` — KV 数据库类：`new Database("name")` → `.get(k)` / `.set(k,v)` / `.delete(k)` / `.listKeys()` / `.searchValue(pattern)` / `.push(k,v)` / `.getArray(k)`
- `req` — 请求对象：`req.query` / `req.params` / `req.body`
- `document.write(str)` — 输出响应内容
- `res` — 响应对象（部分场景可用 `res.write()` / `res.end()`）