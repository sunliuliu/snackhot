import { Outlet, NavLink, Link } from 'react-router-dom'

function todayStr() {
  const d = new Date()
  const w = ['日','一','二','三','四','五','六'][d.getDay()]
  return `${d.getFullYear()}.${String(d.getMonth()+1).padStart(2,'0')}.${String(d.getDate()).padStart(2,'0')} · 周${w}`
}

const TABS = [
  { to: '/',            label: '最新精选', end: true },
  { to: '/hot',         label: '热点榜' },
  { to: '/daily',       label: '每日早报' },
  { to: '/leaderboard', label: '排行榜' },
  { to: '/fresh',       label: '新鲜零食' },
  { to: '/all',         label: '全部动态' },
]

export default function App() {
  return (
    <div className="min-h-screen bg-bg-page">
      {/* 顶栏 */}
      <div className="site-wrap top-bar">
        <Link to="/" className="top-bar-brand">
          <span className="logo-mark">🌰</span>
          <span>SnackHot</span>
        </Link>
        <span className="text-[12px] text-ink-500 hidden sm:inline tracking-wide">零食行业 AI 雷达</span>
        <span className="ml-auto text-[12px] text-ink-400 font-mono tabular-nums">{todayStr()}</span>
      </div>

      {/* Tab 导航 */}
      <div className="site-wrap tab-bar">
        {TABS.map(t => (
          <NavLink
            key={t.to}
            to={t.to}
            end={t.end}
            className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}
          >{t.label}</NavLink>
        ))}
      </div>

      {/* 主内容 */}
      <main className="site-wrap pb-20">
        <Outlet />
      </main>

      {/* 底部 */}
      <footer className="site-wrap py-12 border-t border-ink-200">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 text-[13px] font-semibold text-ink-700 mb-2">
            <span className="logo-mark !w-4 !h-4 !text-[10px]">🌰</span>
            SnackHot
          </div>
          <p className="text-[12px] text-ink-400">每 2 小时自动扫描 30+ 零食行业信源</p>
          <p className="text-[11px] text-ink-300 mt-2">数据仅供行业参考 · 不构成投资建议 · 本站仅做技术演示</p>
        </div>
      </footer>
    </div>
  )
}