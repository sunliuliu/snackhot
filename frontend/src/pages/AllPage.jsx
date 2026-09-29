import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'

const CAT_LIST = [
  { value:'all', label:'全部分类' },
  { value:'财报业绩', label:'财报业绩' },
  { value:'渠道变革', label:'渠道变革' },
  { value:'新品发布', label:'新品发布' },
  { value:'食品安全', label:'食品安全' },
  { value:'供应链变动', label:'供应链变动' },
  { value:'跨界联名', label:'跨界联名' },
  { value:'营销动态', label:'营销动态' },
  { value:'行业政策', label:'行业政策' },
  { value:'新鲜零食', label:'新鲜零食' },
]

export default function AllPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [keyword, setKeyword] = useState('')
  const [cat, setCat] = useState('all')

  useEffect(() => {
    api.getItems({ mode:'all', limit:200 }).then(d => {
      setItems(d?.items || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="py-20 text-center text-[rgb(130,140,145)]">加载中...</div>

  let filtered = items
  if (keyword.trim()) filtered = filtered.filter(i => (i.title || '').includes(keyword) || (i.summary || '').includes(keyword))
  if (cat !== 'all') filtered = filtered.filter(i => i.event_type === cat)

  return (
    <div>
      <h1 className="page-title">全部动态</h1>
      <p className="page-sub">共 {items.length} 条 · 爬虫覆盖 30+ 信源 · 每 2 小时更新</p>

      {/* 搜索 + 筛选 */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          placeholder="搜索资讯标题或摘要..."
          value={keyword}
          onChange={e => setKeyword(e.target.value)}
          className="flex-1 px-3 py-2 text-[13px] border border-[rgb(223,228,225)] bg-white focus:border-[rgb(32,42,48)] focus:outline-none"
        />
        <select value={cat} onChange={e => setCat(e.target.value)}
                className="px-3 py-2 text-[13px] border border-[rgb(223,228,225)] bg-white">
          {CAT_LIST.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
      </div>

      {(keyword || cat !== 'all') && (
        <div className="text-[12px] text-[rgb(130,140,145)] mb-3 flex items-center gap-2">
          筛选结果：{filtered.length} / {items.length} 条
          {(keyword || cat !== 'all') && (
            <button onClick={() => { setKeyword(''); setCat('all') }} className="hover:text-[rgb(23,107,117)] underline">清除筛选</button>
          )}
        </div>
      )}

      {filtered.length === 0 ? (
        <div className="py-20 text-center text-[rgb(130,140,145)]">没有找到匹配的资讯</div>
      ) : filtered.map((item, idx) => (
        <Link key={item.id} to={`/items/${item.id}`}
              className="clickable-item block py-3 border-b border-[rgb(223,228,225)] last:border-b-0 hover:bg-[rgb(249,249,246)] transition-colors">
          <div className="flex items-start gap-3">
            <span className="shrink-0 font-mono text-[12px] text-[rgb(130,140,145)] pt-0.5 w-6 text-right">{idx+1}.</span>
            <div className="flex-1 min-w-0">
              <h4 className="text-[14px] font-medium leading-[1.5] text-[rgb(32,42,48)]">{item.title}</h4>
              {item.summary && <p className="mt-1 text-[12.5px] text-[rgb(130,140,145)] line-clamp-1">{item.summary}</p>}
              <div className="mt-1 flex items-center gap-2 text-[11px] text-[rgb(130,140,145)]">
                <span>{item.source_name}</span>
                {item.event_type && <span>· {item.event_type}</span>}
                {item.category && <span>· {item.category}</span>}
                <span className="ml-auto">{item.published_at ? new Date(item.published_at).toLocaleString('zh-CN', { month:'numeric', day:'numeric', hour:'2-digit', minute:'2-digit' }) : ''}</span>
              </div>
            </div>
            <div className="shrink-0 font-mono text-[13px] font-bold text-[rgb(48,60,66)] tabular-nums pt-0.5">{item.score}</div>
          </div>
        </Link>
      ))}
    </div>
  )
}