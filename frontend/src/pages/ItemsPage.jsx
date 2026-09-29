import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'

const CATEGORIES = [
  { key: 'all',       label: '全部',      color: '#1C1917' },
  { key: '财报业绩',   label: '财报业绩',   color: '#EA580C' },
  { key: '渠道变革',   label: '渠道变革',   color: '#0891B2' },
  { key: '新品发布',   label: '新品发布',   color: '#16A34A' },
  { key: '食品安全',   label: '食品安全',   color: '#DC2626' },
  { key: '供应链变动', label: '供应链',     color: '#7C3AED' },
  { key: '跨界联名',   label: '跨界联名',   color: '#DB2777' },
  { key: '营销动态',   label: '营销动态',   color: '#F59E0B' },
  { key: '行业政策',   label: '行业政策',   color: '#1E40AF' },
  { key: '新鲜零食',   label: '新鲜零食',   color: '#EA580C' },
]

function categoryChip(key) {
  return CATEGORIES.find(c => c.key === key) || CATEGORIES[0]
}

export default function ItemsPage() {
  const [events, setEvents] = useState([])
  const [allItems, setAllItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [openCards, setOpenCards] = useState({})
  const [activeCat, setActiveCat] = useState('all')

  useEffect(() => {
    Promise.all([
      api.getHotTopics(),
      api.getItems({ mode:'all', limit:100 }),
    ]).then(([eData, iData]) => {
      setEvents(eData?.hot_topics || [])
      setAllItems(iData?.items || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const toggleCard = (id) => setOpenCards(p => ({ ...p, [id]: !p[id] }))
  const filteredItems = activeCat === 'all' ? allItems : allItems.filter(i => i.event_type === activeCat)

  if (loading) return <Loading />

  return (
    <div className="animate-fade-in">
      {/* ========== 当前热点分区 ========== */}
      <section className="mb-12">
        <div className="flex items-baseline justify-between mb-5">
          <h2 className="section-title">🔥 当前热点</h2>
          <Link to="/hot" className="text-[12px] text-ink-400 hover:text-brand-500 transition-colors font-medium">
            查看完整榜单 →
          </Link>
        </div>

        {events.length === 0 ? (
          <EmptyHint text="暂无热点 · 爬虫可能还未运行" />
        ) : events.slice(0, 3).map((evt, idx) => (
          <EventCard key={evt.id} evt={evt} rank={idx + 1}
                     open={!!openCards[evt.id]} onToggle={() => toggleCard(evt.id)}
                     delay={idx * 0.05} />
        ))}
      </section>

      {/* ========== 最新精选分区 ========== */}
      <section>
        <div className="flex items-baseline justify-between mb-4">
          <h2 className="section-title">📰 最新精选</h2>
          <Link to="/all" className="text-[12px] text-ink-400 hover:text-brand-500 transition-colors font-medium">
            查看全部 →
          </Link>
        </div>

        {/* Category 筛选条 */}
        <div className="flex flex-wrap gap-1.5 mb-5 pb-2 border-b border-ink-200">
          {CATEGORIES.map(c => (
            <button
              key={c.key}
              onClick={() => setActiveCat(c.key)}
              className={`px-3 py-1.5 text-[12px] font-medium transition-all rounded-[6px] ${
                activeCat === c.key
                  ? 'bg-ink-900 text-white shadow-soft'
                  : 'text-ink-500 hover:text-ink-800 hover:bg-ink-100'
              }`}
            >{c.label}</button>
          ))}
        </div>

        {/* 精选列表 */}
        {filteredItems.length === 0 ? (
          <EmptyHint text="该分类下暂无资讯" />
        ) : filteredItems.map((item, idx) => (
          <ItemRow key={item.id} item={item} rank={idx + 1} />
        ))}
      </section>
    </div>
  )
}

// ============ 事件大卡 ============
function EventCard({ evt, rank, open, onToggle, delay = 0 }) {
  const hotIndex = Math.round(evt.hot_score || 0)
  const trend = evt.trend || '+5'
  const brands = evt.brand_tags || []
  const sourceCount = evt.source_count || 0
  const signalCount = evt.signal_count || 0
  const otherSources = Math.max(0, sourceCount - 1)
  const cc = categoryChip(evt.event_type)

  return (
    <div className="hot-card" style={{ animationDelay: `${delay}s` }}>
      {/* 精选装饰条（只有前 2 张显示） */}
      {rank <= 2 && <div className="selected-ribbon">精选</div>}

      <div className="flex items-start gap-5">
        {/* 左侧主体 */}
        <div className="flex-1 min-w-0">
          {/* meta 顶行 */}
          <div className="flex items-center gap-2 text-[12px] text-ink-400 leading-[18px] mb-1.5">
            <span className="truncate font-medium text-ink-500">
              {(evt.member_items?.[0]?.source_name) || (brands[0] || '综合')}
            </span>
            <span className="cat-chip" style={{ background: cc.color + '14', color: cc.color }}>{evt.event_type || '行业'}</span>
            <span className="ml-auto"></span>
            <span className="ai-score-badge">
              <span>AI</span>
              <span className="score-num">{evt.ai_score || 75}</span>
            </span>
          </div>

          {/* 大标题 */}
          <h3 className="mt-2 text-[17px] font-semibold leading-[1.5] text-ink-900 tracking-[-0.01em]">
            {evt.title}
          </h3>

          {/* AI 摘要 */}
          {(evt.summary || evt.member_items?.[0]?.summary) && (
            <p className="mt-2 text-[14px] leading-[1.7] text-ink-500">
              {evt.summary || evt.member_items?.[0]?.summary}
            </p>
          )}

          {/* 最新进展 */}
          <div className="mt-3 flex items-center gap-2 text-[12.5px] leading-relaxed">
            <span className="shrink-0 font-semibold text-brand-500">最新进展</span>
            <span className="shrink-0 text-ink-400 font-mono text-[11px]">
              {evt.last_seen_at
                ? new Date(evt.last_seen_at).toLocaleString('zh-CN', { month:'numeric', day:'numeric', hour:'2-digit', minute:'2-digit' })
                : '刚刚'}
            </span>
            <span className="truncate text-ink-500">
              {evt.member_items?.[0]?.title?.slice(0, 45) || '持续发酵中'}
            </span>
          </div>

          {/* 交叉信源 + 展开 */}
          <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[12px]">
            {otherSources > 0 && (
              <button onClick={onToggle} className="inline-flex items-center gap-1 text-ink-400 hover:text-brand-500 transition-colors font-medium">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 12h16M12 4v16"/></svg>
                另有 {otherSources} 家信源报道
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`transition-transform duration-200 ${open ? 'rotate-180' : ''}`}><path d="M6 9l6 6 6-6"/></svg>
              </button>
            )}
            {signalCount > 1 && <span className="text-ink-400">{signalCount} 条进展</span>}
            {brands.slice(0, 3).map(b => (
              <span key={b} className="text-ink-400">· {b}</span>
            ))}
          </div>

          {/* 展开的多条报道 */}
          {open && evt.member_items?.length > 1 && (
            <div className="mt-4 border-t border-ink-200 pt-4 space-y-2 animate-fade-in">
              {evt.member_items.slice(1).map((m, i) => (
                <a key={i} href={m.url} target="_blank" rel="noopener noreferrer"
                   className="flex items-start gap-3 text-[13px] leading-[1.55] group">
                  <span className="shrink-0 text-[11px] text-ink-400 mt-0.5 w-20 truncate font-medium group-hover:text-brand-500">{m.source_name}</span>
                  <span className="line-clamp-1 text-ink-700 group-hover:text-brand-500 transition-colors">{m.title}</span>
                </a>
              ))}
            </div>
          )}

          {/* 推荐理由 chip */}
          <div className="mt-3 bg-bg-sunk border-l-2 border-brand-500 px-3 py-2 rounded-r-lg">
            <p className="text-[12.5px] leading-[1.7] text-ink-500 italic">
              💡 {evt.reason || `覆盖 ${brands.slice(0,3).join('、')} 等 ${brands.length} 个头部品牌的${evt.event_type || '行业'}相关进展，${sourceCount} 个信源交叉验证。`}
            </p>
          </div>
        </div>

        {/* 右侧热度指数 + 涨幅 */}
        <div className="hot-index-display shrink-0">
          <div className="hot-index-num">{hotIndex}</div>
          {trend && (
            <div className="trend-chip mt-1">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4l8 10H4z"/></svg>
              {trend}
            </div>
          )}
          <div className="hot-index-label">热度指数</div>
          {/* 迷你进度条 */}
          <div className="heat-bar mt-2 max-w-[60px] ml-auto">
            <div className="heat-bar-fill" style={{ width: `${Math.min(100, hotIndex / 6)}%` }}></div>
          </div>
        </div>
      </div>
    </div>
  )
}

// ============ 资讯行 ============
function ItemRow({ item, rank }) {
  const published = item.published_at
    ? new Date(item.published_at).toLocaleString('zh-CN', { month:'numeric', day:'numeric', hour:'2-digit', minute:'2-digit' })
    : ''
  const cc = categoryChip(item.event_type)
  const scoreColor = item.score >= 80 ? '#EA580C' : item.score >= 65 ? '#292524' : '#78716C'

  return (
    <Link to={`/items/${item.id}`} className="clickable-item flex items-start gap-3">
      {/* 排名 */}
      <span className="shrink-0 font-mono text-[12px] text-ink-300 pt-0.5 w-6 text-right tabular-nums">{String(rank).padStart(2,'0')}</span>

      {/* 主体 */}
      <div className="flex-1 min-w-0">
        <h4 className="text-[14px] font-medium leading-[1.55] text-ink-800 group-hover:text-brand-500 transition-colors">
          {item.title}
        </h4>
        <div className="mt-1 flex items-center gap-1.5 flex-wrap text-[11.5px] text-ink-400">
          <span className="font-medium text-ink-500">{item.source_name}</span>
          <span className="text-ink-200">·</span>
          <span className="cat-chip !text-[10px] !px-2 !py-0" style={{ background: cc.color + '14', color: cc.color }}>{item.event_type}</span>
          {item.brand_tags?.slice(0,2).map(b => <span key={b} className="text-ink-400">{b}</span>)}
          <span className="ml-auto">{published}</span>
        </div>
      </div>

      {/* AI 分数（根据分数变色） */}
      <div className="shrink-0 font-mono text-[14px] font-bold tabular-nums pt-0.5" style={{ color: scoreColor }}>
        {item.score}
      </div>
    </Link>
  )
}

// ============ 加载骨架 ============
function Loading() {
  return (
    <div className="space-y-3 animate-fade-in">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="bg-white border border-ink-100 rounded-card p-5">
          <div className="flex items-center gap-2 mb-3">
            <div className="skeleton h-[14px] w-20"></div>
            <div className="skeleton h-[14px] w-14"></div>
          </div>
          <div className="skeleton h-[18px] w-4/5 mb-2"></div>
          <div className="skeleton h-[13px] w-full mb-1.5"></div>
          <div className="skeleton h-[13px] w-3/5"></div>
        </div>
      ))}
    </div>
  )
}

// ============ 空状态 ============
function EmptyHint({ text }) {
  return (
    <div className="empty-state">
      <div className="icon">🌰</div>
      <p className="text-[13px]">{text}</p>
    </div>
  )
}