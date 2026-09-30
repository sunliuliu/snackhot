import { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function HotTopicsPage() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getHotTopics().then(d => {
      setEvents(d?.hot_topics || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-20 text-[rgb(130,140,145)]">加载中...</div>
  if (!events.length) return <div className="text-center py-20 text-[rgb(130,140,145)]">暂无热点事件</div>

  return (
    <div>
      <h1 className="page-title">🔥 零食行业热点榜</h1>
      <p className="page-sub">按 AI 热度指数自动生成 · Top {events.length}</p>

      {events.map((evt, idx) => (
        <EventRow key={evt.id} evt={evt} rank={idx + 1} />
      ))}
    </div>
  )
}

function EventRow({ evt, rank }) {
  const hotIndex = Math.round(evt.hot_score || 0)
  const trend = evt.trend || ''

  return (
    <div className="hot-card relative">
      <div className="flex items-start gap-4">
        {/* 排名 */}
        <div className="shrink-0 pt-0.5">
          {rank <= 3 ? (
            <span className="font-extrabold font-mono leading-none"
                  style={{ fontSize: rank === 1 ? '48px' : rank === 2 ? '36px' : '28px',
                           color: rank === 1 ? '#d97706' : rank === 2 ? '#9ca3af' : '#ea580c',
                           letterSpacing: '-2px' }}>#{rank}</span>
          ) : (
            <span className="font-semibold font-mono text-[13px] text-[rgb(130,140,145)]">{rank}</span>
          )}
        </div>

        {/* 内容 */}
        <div className="flex-1 min-w-0">
          <h3 className="text-[15px] font-semibold leading-[1.45] mb-1" style={{ color:'rgb(32,42,48)' }}>
            {evt.title}
          </h3>
          <div className="flex items-center gap-2 text-[12px] text-[rgb(130,140,145)]">
            <span>{evt.source_count || 0} 信源</span>
            <span>·</span>
            <span>{evt.signal_count || 0} 报道</span>
            {evt.event_type && <><span>·</span><span>{evt.event_type}</span></>}
            {(evt.brand_tags || []).slice(0, 2).map(b => (
              <span key={b} className="bg-[rgb(243,243,239)] text-[rgb(89,101,107)] px-1.5 py-0.5 rounded-full text-[10.5px]">{b}</span>
            ))}
          </div>
        </div>

        {/* 热度指数 + 涨幅 */}
        <div className="shrink-0 text-right pt-0.5">
          <div className="font-mono font-semibold text-[18px] leading-none tabular-nums text-[rgb(48,60,66)]">
            {hotIndex}
          </div>
          {trend && (
            <div className="mt-0.5 text-[10.5px] font-medium text-[rgb(180,83,9)]">{trend}</div>
          )}
        </div>
      </div>
    </div>
  )
}