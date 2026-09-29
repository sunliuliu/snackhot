import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'

export default function FreshSnackPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    console.log('[FreshSnackPage] useEffect fired')
    api.getItems({ mode: 'all', limit: 200 }).then(d => {
      console.log('[FreshSnackPage] api raw response:', d ? Object.keys(d) : 'null')
      const all = Array.isArray(d?.items) ? d.items : []
      console.log('[FreshSnackPage] all items:', all.length)

      const fresh_kw = ['新鲜零食','新鲜','鲜食','鲜货','锁鲜','短保','现做','鲜切','烘焙',
        '金粒门','鲜目录','鲜装','便利店','面包','鲜卤','果汁','钟薛高','冰淇淋',
        '鲜奶','茶饮','DQ','冷冻食品','冷链','鲜榨','鲜果','雪糕','冷冻','低温']

      const filtered = []
      for (let i = 0; i < all.length; i++) {
        const it = all[i]
        if (!it || typeof it !== 'object') continue
        if (it.category === '新鲜零食') { filtered.push(it); continue }
        const t = String(it.title || '')
        const s = String(it.summary || '')
        const e = String(it.event_type || '')
        const b = Array.isArray(it.brand_tags) ? it.brand_tags.join(' ') : String(it.brand_tags || '')
        const hay = (t + s + e + ' ' + b).toLowerCase()
        if (fresh_kw.some(k => hay.includes(k.toLowerCase()))) {
          filtered.push(it)
        }
      }

      console.log('[FreshSnackPage] filtered:', filtered.length)
      filtered.sort((a, b) => (Number(b.score) || 0) - (Number(a.score) || 0))
      setItems(filtered)
      setLoading(false)
    }).catch(e => {
      console.error('[FreshSnackPage] api ERROR:', e)
      setLoading(false)
    })
  }, [])

  if (loading) return <div className="py-20 text-center text-[rgb(130,140,145)]">加载中...</div>

  return (
    <div>
      <h1 className="page-title">🥐 新鲜零食动态</h1>
      <p className="page-sub">短保 · 锁鲜 · 现做 · 鲜切 · 烘焙 · 便利店鲜食 · 共 {items.length} 条</p>

      <div className="flex flex-wrap gap-2 mb-6 text-[11px]">
        {['新鲜烘焙','锁鲜装','鲜切水果','现做卤味','便利店鲜食','短保面包','鲜货集合店','冷萃茶饮','鲜奶制品'].map(t => (
          <span key={t} className="px-2 py-0.5 border border-[rgb(223,228,225)] text-[rgb(89,101,107)]">{t}</span>
        ))}
      </div>

      {items.length === 0 ? (
        <div className="py-20 text-center text-[rgb(130,140,145)] text-[13px]">暂未抓到新鲜零食赛道的资讯，下次爬取会覆盖更多关键词</div>
      ) : (
        <div className="divide-y divide-[rgb(223,228,225)] border-t border-[rgb(223,228,225)]">
          {items.map((it) => (
            <Link key={it.id || it.title} to={"/items/" + (it.id || '')} className="block py-4 group">
              <div className="flex items-center gap-2 mb-1.5 text-[11px]">
                <span className="text-[rgb(130,140,145)]">{it.source_name}</span>
                {it.score != null && <span className="font-mono text-[rgb(32,42,48)] font-semibold">AI {it.score}</span>}
                {it.event_type && <span className="px-1.5 py-0.5 bg-[rgb(245,245,244)] text-[rgb(89,101,107)] text-[10px]">{it.event_type}</span>}
                {Array.isArray(it.brand_tags) && it.brand_tags.length > 0 && (
                  <span className="text-[rgb(130,140,145)]">· {it.brand_tags.slice(0,3).join('/')}</span>
                )}
              </div>
              <h3 className="text-[15px] leading-[1.55] text-[rgb(32,42,48)] group-hover:text-[rgb(220,38,38)] transition-colors">{it.title}</h3>
              {it.summary && (
                <p className="mt-1 text-[12.5px] leading-[1.7] text-[rgb(130,140,145)] line-clamp-2">{it.summary}</p>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
