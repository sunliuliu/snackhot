import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { DailySkeleton } from '../components/Skeleton.jsx'

function formatISO(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

export default function DailyPage() {
  const [offset, setOffset] = useState(0)
  const [daily, setDaily] = useState(null)
  const [loading, setLoading] = useState(true)

  const target = new Date(Date.now() + offset * 86400000)

  useEffect(() => {
    setLoading(true)
    api.getDaily(formatISO(target)).then(d => {
      setDaily(d?.daily || null)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [offset])

  return (
    <div>
      <h1 className="page-title">📰 零食行业每日早报</h1>
      <p className="page-sub">AI 自动生成 · 每 2 小时更新</p>

      {/* 日期导航 */}
      <div className="flex items-center justify-center gap-4 py-4 mb-6 text-[12px]">
        <button onClick={() => setOffset(offset - 1)} className="px-3 py-1 border border-[rgb(223,228,225)] hover:border-[rgb(32,42,48)] text-[rgb(89,101,107)] hover:text-[rgb(32,42,48)] transition-colors">← 前一天</button>
        <span className="font-mono font-semibold text-[rgb(32,42,48)] px-2">{formatISO(target)}</span>
        <button onClick={() => setOffset(Math.min(offset + 1, 0))} disabled={offset >= 0} className="px-3 py-1 border border-[rgb(223,228,225)] hover:border-[rgb(32,42,48)] text-[rgb(89,101,107)] hover:text-[rgb(32,42,48)] transition-colors disabled:opacity-30 disabled:cursor-not-allowed">后一天 →</button>
      </div>

      {loading ? <DailySkeleton /> : !daily ? (
        <div className="text-center py-20 text-[rgb(130,140,145)] text-[13px] space-y-1">
          <p>该日期早报尚未生成</p>
          <p className="text-[12px]">每 2 小时自动生成</p>
        </div>
      ) : <DailyContent daily={daily} />}
    </div>
  )
}

function DailyContent({ daily }) {
  const itemCount = daily.item_count || 0
  const eventCount = daily.event_count || 0
  const topEvents = daily.top_events || []
  const generatedAt = daily.generated_at ? new Date(daily.generated_at).toLocaleString('zh-CN') : ''

  return (
    <>
      {/* 统计卡 */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatCard label="今日资讯" value={itemCount} suffix="条" emoji="📋" />
        <StatCard label="热点事件" value={eventCount} suffix="个" emoji="🔥" />
        <StatCard label="生成时间" value="" suffix={generatedAt.split(' ')[1]?.slice(0, 5) || ''} emoji="⏰" sub={generatedAt.split(' ')[0]} />
      </div>

      {/* Top 热点事件 */}
      {topEvents.length > 0 && (
        <section className="mb-8">
          <div className="text-[10.5px] font-semibold tracking-[2px] text-[rgb(130,140,145)] mb-4 uppercase">🔥 今日热点事件 Top {topEvents.length}</div>
          <div className="border-t border-[rgb(223,228,225)]">
            {topEvents.map((e, i) => (
              <div key={i} className="flex items-start gap-4 py-3 border-b border-[rgb(223,228,225)] hover:bg-[rgb(249,249,247)] transition-colors">
                <span className={"shrink-0 font-extrabold font-mono text-[18px] leading-none pt-0.5 " + (i === 0 ? 'text-[#d97706]' : i < 3 ? 'text-[#9ca3af]' : 'text-[rgb(130,140,145)]')}>
                  #{i + 1}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="text-[14px] leading-[1.6]" style={{ color: 'rgb(32,42,48)' }}>{e.title}</div>
                </div>
                {e.score && (
                  <span className="shrink-0 font-mono text-[13px] text-[rgb(130,140,145)]">热度 {Math.round(e.score)}</span>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      <div className="text-center text-[11px] text-[rgb(160,170,175)] mt-8">
        数据来源: 11 个食品行业信源 · AI 自动聚合分析 · 每 2 小时更新
      </div>
    </>
  )
}

function StatCard({ label, value, suffix, emoji, sub }) {
  return (
    <div className="bg-[rgb(249,249,247)] rounded-xl px-5 py-4">
      <div className="flex items-center gap-2 text-[11px] font-semibold tracking-[1px] text-[rgb(130,140,145)] uppercase mb-2">
        <span>{emoji}</span>
        <span>{label}</span>
      </div>
      <div className="font-mono font-bold text-[28px] leading-none text-[rgb(32,42,48)]">
        {value}{suffix && <span className="text-[14px] text-[rgb(130,140,145)] ml-1">{suffix}</span>}
      </div>
      {sub && <div className="text-[11px] text-[rgb(160,170,175)] mt-1">{sub}</div>}
    </div>
  )
}
