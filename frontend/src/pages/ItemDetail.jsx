import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api.js'

export default function ItemDetail() {
  const { id } = useParams()
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getItems({ mode:'all', limit:100 }).then(d => {
      const list = d?.items || []
      const found = list.find(i => i.id === id) || list[0]
      setItem(found || null)
      setLoading(false)
    })
  }, [id])

  if (loading) return <div className="text-center py-20 text-[rgb(130,140,145)]">加载中...</div>
  if (!item) return (
    <div className="text-center py-20">
      <p className="text-[rgb(130,140,145)] mb-4">该资讯不存在</p>
      <Link to="/" className="text-[rgb(32,42,48)] hover:underline">← 返回</Link>
    </div>
  )

  return (
    <div className="max-w-[720px] mx-auto">
      <Link to="/" className="inline-block text-[12px] text-[rgb(130,140,145)] hover:text-[rgb(32,42,48)] mb-6">← 返回</Link>

      {/* meta */}
      <div className="flex items-center gap-2 mb-3 text-[12px] text-[rgb(130,140,145)]">
        <span className="meta-chip">{item.source_name}</span>
        <span>·</span>
        <span>AI 评分 {item.score}</span>
        {item.category && <><span>·</span><span>{item.category}</span></>}
        {item.event_type && <><span>·</span><span>{item.event_type}</span></>}
      </div>

      <h1 className="font-bold text-[22px] leading-[1.35] mb-5" style={{ color:'rgb(32,42,48)' }}>{item.title}</h1>

      {item.brand_tags?.length > 0 && (
        <div className="flex gap-2 mb-5 text-[12px] text-[rgb(89,101,107)]">
          {item.brand_tags.map(b => <span key={b}>#{b}</span>)}
        </div>
      )}

      {/* AI 摘要 */}
      <section className="border-l-[3px] border-[rgb(32,42,48)] pl-4 my-6">
        <div className="text-[10.5px] font-semibold tracking-[2px] uppercase text-[rgb(130,140,145)] mb-2">AI 摘要</div>
        <p className="text-[15px] leading-[1.9]" style={{ color:'rgb(48,60,66)' }}>{item.summary}</p>
      </section>

      {item.reason && (
        <p className="text-[13px] text-[rgb(89,101,107)] italic mb-8">— {item.reason}</p>
      )}

      <a href={item.url} target="_blank" rel="noopener noreferrer"
         className="inline-flex items-center gap-2 px-4 py-2 bg-[rgb(32,42,48)] text-white text-[13px] font-medium hover:bg-[rgb(48,60,66)] transition-colors">
        查看原文 →
      </a>
    </div>
  )
}