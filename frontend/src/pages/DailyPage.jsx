import { useEffect, useState } from 'react'
import { api } from '../api.js'

function formatISO(d) {
  const y=d.getFullYear(), m=String(d.getMonth()+1).padStart(2,'0'), day=String(d.getDate()).padStart(2,'0')
  return `${y}-${m}-${day}`
}

export default function DailyPage() {
  const [tab, setTab] = useState('daily')
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
      <p className="page-sub">AI 自动生成 · 每日 08:00 更新</p>

      {/* 早/周/月 tab */}
      <div className="tab-bar">
        {[
          { k:'daily',   label:'日报' },
          { k:'weekly',  label:'周报' },
          { k:'monthly', label:'月报' },
        ].map(t => (
          <button key={t.k} onClick={()=>setTab(t.k)} className={`tab ${tab===t.k?'active':''}`}>{t.label}</button>
        ))}
      </div>

      {/* 日期导航 */}
      <div className="flex items-center justify-center gap-4 py-4 mb-6 text-[12px]">
        <button onClick={()=>setOffset(offset-1)} className="px-3 py-1 border border-[rgb(223,228,225)] hover:border-[rgb(32,42,48)] text-[rgb(89,101,107)] hover:text-[rgb(32,42,48)] transition-colors">← 前一天</button>
        <span className="font-mono font-semibold text-[rgb(32,42,48)] px-2">{formatISO(target)}</span>
        <button onClick={()=>setOffset(Math.min(offset+1,0))} disabled={offset>=0} className="px-3 py-1 border border-[rgb(223,228,225)] hover:border-[rgb(32,42,48)] text-[rgb(89,101,107)] hover:text-[rgb(32,42,48)] transition-colors disabled:opacity-30 disabled:cursor-not-allowed">后一天 →</button>
      </div>

      {loading ? <div className="text-center py-20 text-[rgb(130,140,145)]">加载中...</div> : !daily ? (
        <div className="text-center py-20 text-[rgb(130,140,145)] text-[13px] space-y-1">
          <p>该日期早报尚未生成</p>
          <p className="text-[12px]">每日 08:00 自动生成</p>
        </div>
      ) : (
        <>
          {/* 快讯头版 */}
          {daily.highlights?.length > 0 && (
            <section className="mb-8">
              <div className="text-[10.5px] font-semibold tracking-[2px] text-[rgb(130,140,145)] mb-4 uppercase">今日核心快讯</div>
              <ol className="space-y-3 list-decimal list-inside text-[14px] leading-[1.7]" style={{ color:'rgb(32,42,48)' }}>
                {daily.highlights.map((h,i)=>(
                  <li key={i}>{h}</li>
                ))}
              </ol>
            </section>
          )}

          {/* 分类 */}
          {daily.sections?.length > 0 && (
            <section>
              <div className="text-[10.5px] font-semibold tracking-[2px] text-[rgb(130,140,145)] mb-4 uppercase">分类速览</div>
              <div className="border-t border-[rgb(223,228,225)]">
                {daily.sections.map(s => (
                  <div key={s.category} className="flex gap-5 py-4 border-b border-[rgb(223,228,225)]">
                    <div className="w-[110px] shrink-0">
                      <div className="font-semibold text-[13px]" style={{ color:'rgb(32,42,48)' }}>{s.category}</div>
                      <div className="text-[12px] text-[rgb(130,140,145)]">{s.count} 条</div>
                    </div>
                    <ul className="flex-1 space-y-1.5 text-[13.5px]" style={{ color:'rgb(48,60,66)' }}>
                      {s.headlines.map((h,i)=>(
                        <li key={i} className="truncate">· {h}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  )
}