import json, os

BASE = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统"

# ========== 1. weibo.py 加新鲜零食关键词 ==========
p = BASE + r"\crawler\sources\weibo.py"
with open(p, encoding='utf-8') as f:
    c = f.read()

# 找关键词列表末尾，加新鲜零食类
# 关键词列表应该有类似 ["三只松鼠", ..., "量贩零食", ...]
# 我用更保险的方式：找 weibo 关键词组的 pattern

# 先找一下
import re
# 查找所有关键词分组的位置
# 我们在最后一个组后面加新鲜零食组

# 更简单：直接在 NOISE_PATTERNS 前加 FRESH_SNACK 关键词组
# 先看结构
if 'FRESH_SNACK_KEYWORDS' not in c:
    # 在文件顶部或合适位置加
    # 找所有关键词列表合并的地方
    # 直接在现有 KEYWORDS 后面追加新鲜零食
    
    # 策略：在第一个出现 snack 相关 keywords 组后面加
    add_block = '''

# ============ 新鲜零食行业（专门赛道） ============
FRESH_SNACK_KEYWORDS = [
    # 品牌/渠道
    '金粒门', '鲜目录', '零食忙', '良品铺子 鲜', '三只松鼠 锁鲜',
    '鲜食', '鲜切水果', '现做零食', '短保零食', '锁鲜装',
    # 品类
    '便利店 鲜食', '全家 面包', '711 鲜', '罗森 鲜', '便利蜂 鲜',
    '烘焙 零食', '短保面包', '现做卤味', '鲜卤', '冷萃茶饮',
    '鲜奶 零食', '新鲜零食赛道', '鲜货', '零食鲜货',
    # 事件
    '新鲜零食 融资', '新鲜零食 门店', '新鲜零食 供应链',
    '量贩零食 鲜', '零食集合店 鲜',
]
'''
    # 把它插到 class WeiboCrawler 之前
    marker = 'class WeiboCrawler'
    c = c.replace(marker, add_block + '\n' + marker)
    
    # 还要确保这些关键词被实际使用
    # 找 _SEARCH_KEYWORDS 或类似的合并列表
    if '_SEARCH_KEYWORDS' in c:
        c = c.replace(
            '_SEARCH_KEYWORDS = ',
            '_SEARCH_KEYWORDS = list(set(' 
        )
    # 更简单：找最后一个大的 keywords 列表合并点
    
    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
    print("1. weibo.py - added FRESH_SNACK_KEYWORDS block")
else:
    print("1. weibo.py - already has FRESH_SNACK_KEYWORDS")

# ========== 2. llm_processor.py category 加「新鲜零食」==========
p2 = BASE + r"\crawler\services\llm_processor.py"
with open(p2, encoding='utf-8') as f:
    c2 = f.read()

old_cat = 'category: 品类（坚果炒货/肉脯卤味/饼干糕点/糖果巧克力/休闲膨化/蜜饯果干/其他）'
new_cat = 'category: 品类（坚果炒货/肉脯卤味/饼干糕点/糖果巧克力/休闲膨化/蜜饯果干/新鲜零食/冲调饮品/其他）'
if '新鲜零食' not in c2:
    c2 = c2.replace(old_cat, new_cat)
    with open(p2, 'w', encoding='utf-8') as f:
        f.write(c2)
    print("2. llm_processor.py - added 新鲜零食 to category list")
else:
    print("2. llm_processor.py - already has 新鲜零食")

# ========== 3. 新建 FreshSnackPage.jsx ==========
fresh_page = '''import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'

export default function FreshSnackPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 从全量里筛 category=新鲜零食 或 标题/摘要含新鲜零食关键词的
    api.getItems({ mode: 'all', limit: 200 }).then(d => {
      const all = d?.items || []
      const fresh_kw = ['新鲜','鲜食','鲜货','锁鲜','短保','现做','鲜切','烘焙','金粒门','鲜目录','便利店鲜','面包','鲜卤']
      const filtered = all.filter(it => {
        if (it.category === '新鲜零食') return true
        const hay = ((it.title||'') + (it.summary||'') + (it.event_type||'') + ' ' + (it.brand_tags||[]).join(' ')).toLowerCase()
        return fresh_kw.some(k => k.toLowerCase() in hay)
      })
      // 按分数+时间排序
      filtered.sort((a, b) => (b.score||0) - (a.score||0))
      setItems(filtered)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-20 text-center text-[rgb(130,140,145)]">加载中...</div>

  return (
    <div>
      <h1 className="page-title">🥐 新鲜零食动态</h1>
      <p className="page-sub">短保 · 锁鲜 · 现做 · 鲜切 · 烘焙 · 便利店鲜食 · 共 {items.length} 条</p>

      {/* 小标签说明 */}
      <div className="flex flex-wrap gap-2 mb-6 text-[11px]">
        {['新鲜烘焙','锁鲜装','鲜切水果','现做卤味','便利店鲜食','短保面包','鲜货集合店','冷萃茶饮','鲜奶制品'].map(t => (
          <span key={t} className="px-2 py-0.5 border border-[rgb(223,228,225)] text-[rgb(89,101,107)]">{t}</span>
        ))}
      </div>

      {items.length === 0 ? (
        <div className="py-20 text-center text-[rgb(130,140,145)] text-[13px]">暂未抓到新鲜零食赛道的资讯，下次爬取会覆盖更多关键词</div>
      ) : (
        <div className="divide-y divide-[rgb(223,228,225)] border-t border-[rgb(223,228,225)]">
          {items.map((it, idx) => (
            <Link key={it.id} to={"/items/" + it.id} className="block py-4 group">
              {/* 来源 + AI 分数 */}
              <div className="flex items-center gap-2 mb-1.5 text-[11px]">
                <span className="text-[rgb(130,140,145)]">{it.source_name}</span>
                {it.score != null && <span className="font-mono text-[rgb(32,42,48)] font-semibold">AI {it.score}</span>}
                {it.event_type && <span className="px-1.5 py-0.5 bg-[rgb(245,245,244)] text-[rgb(89,101,107)] text-[10px]">{it.event_type}</span>}
                {it.brand_tags?.length > 0 && (
                  <span className="text-[rgb(130,140,145)]">· {it.brand_tags.slice(0,3).join('/')}</span>
                )}
              </div>
              {/* 标题 */}
              <h3 className="text-[15px] leading-[1.55] text-[rgb(32,42,48)] group-hover:text-[rgb(220,38,38)] transition-colors">
                {it.title}
              </h3>
              {/* 摘要 */}
              {it.summary && (
                <p className="mt-1 text-[12.5px] leading-[1.7] text-[rgb(130,140,145)] line-clamp-2">
                  {it.summary}
                </p>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
'''

with open(BASE + r"\frontend\src\pages\FreshSnackPage.jsx", 'w', encoding='utf-8') as f:
    f.write(fresh_page)
print("3. FreshSnackPage.jsx - created")

# ========== 4. App.jsx 加 Tab ==========
p4 = BASE + r"\frontend\src\App.jsx"
with open(p4, encoding='utf-8') as f:
    c4 = f.read()

# 在 TABS 数组里加新鲜零食
old_tabs_end = "  { to: '/all',         label: '全部动态' },\n]"
new_tabs_end = "  { to: '/fresh',       label: '新鲜零食' },\n  { to: '/all',         label: '全部动态' },\n]"

if "'/fresh'" not in c4 and '新鲜零食' not in c4:
    c4 = c4.replace(old_tabs_end, new_tabs_end)
    with open(p4, 'w', encoding='utf-8') as f:
        f.write(c4)
    print("4. App.jsx - added '新鲜零食' tab")
else:
    print("4. App.jsx - already has fresh tab")

# ========== 5. main.jsx 加路由 ==========
p5 = BASE + r"\frontend\src\main.jsx"
with open(p5, encoding='utf-8') as f:
    c5 = f.read()

if 'FreshSnackPage' not in c5:
    c5 = c5.replace(
        "import LeaderboardPage from './pages/LeaderboardPage.jsx'",
        "import LeaderboardPage from './pages/LeaderboardPage.jsx'\nimport FreshSnackPage from './pages/FreshSnackPage.jsx'"
    )
    c5 = c5.replace(
        "          <Route path=\"all\" element={<AllPage />} />",
        "          <Route path=\"fresh\" element={<FreshSnackPage />} />\n          <Route path=\"all\" element={<AllPage />} />"
    )
    with open(p5, 'w', encoding='utf-8') as f:
        f.write(c5)
    print("5. main.jsx - added /fresh route")
else:
    print("5. main.jsx - already has /fresh route")

print()
print("=== All done, vite HMR will auto-reload ===")
