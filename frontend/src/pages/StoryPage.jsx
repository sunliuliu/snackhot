import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api.js'
import ItemCard from '../components/ItemCard.jsx'

export default function StoryPage() {
  const { id } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getStory(id).then(d => {
      setData(d)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [id])

  if (loading) return <div className="card p-8 text-center text-gray-400">加载中...</div>
  if (!data?.event) return <div className="card p-12 text-center text-gray-400">事件不存在</div>

  const { event, members = [] } = data

  return (
    <div className="space-y-6">
      <Link to="/hot-topics" className="text-sm text-brand-600 link-hover">← 返回热点榜</Link>

      <div className="card p-6 space-y-3">
        <div className="flex items-center gap-2 text-xs">
          <span className="rank-num rank-1">#{event.rank}</span>
          <span className={`badge bg-brand-50 text-brand-700 ml-1`}>{event.event_type}</span>
          {event.brand_tags?.map(b => (
            <span key={b} className="text-gray-400">{b}</span>
          ))}
        </div>
        <h1 className="text-xl font-bold">{event.title}</h1>
        {event.summary && <p className="text-gray-600">{event.summary}</p>}
        <div className="flex gap-4 text-xs text-gray-400 pt-2 border-t border-gray-100">
          <span>{event.source_count} 信源交叉报道</span>
          <span>{event.signal_count} 条报道</span>
          <span className="ml-auto">热度分 {event.hot_score}</span>
        </div>
      </div>

      <div className="space-y-2">
        <h2 className="text-sm font-medium text-gray-500">相关报道（{members.length}）</h2>
        {members.map(m => <ItemCard key={m.id} item={m} />)}
      </div>
    </div>
  )
}
