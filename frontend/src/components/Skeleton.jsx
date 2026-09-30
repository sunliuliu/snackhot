// Skeleton Loading 组件 — 全站通用
export function ItemSkeleton({ count = 8 }) {
  return (
    <div>
      {Array.from({ length: count }).map((_, i) => (
        <div className="skel-item" key={i}>
          <div className="skeleton skel-title" />
          <div className="skeleton skel-meta" />
          <div className="skeleton skel-summary" />
          <div className="skeleton skel-summary" />
        </div>
      ))}
    </div>
  )
}

export function HotTopicsSkeleton({ count = 6 }) {
  return (
    <div>
      {Array.from({ length: count }).map((_, i) => (
        <div className="skel-hot" key={i}>
          <div className="skeleton skel-hot-rank" />
          <div style={{ flex: 1 }}>
            <div className="skeleton skel-hot-title" />
            <div className="skeleton skel-hot-meta" />
          </div>
          <div className="skeleton skel-hot-score" />
        </div>
      ))}
    </div>
  )
}

export function DailySkeleton() {
  return (
    <div>
      {/* 统计卡 */}
      <div className="skel-daily-stat">
        <div className="skel-daily-stat-item"><div className="skeleton skel-daily-stat-num"/><div className="skeleton skel-daily-stat-label"/></div>
        <div className="skel-daily-stat-item"><div className="skeleton skel-daily-stat-num"/><div className="skeleton skel-daily-stat-label"/></div>
        <div className="skel-daily-stat-item"><div className="skeleton skel-daily-stat-num"/><div className="skeleton skel-daily-stat-label"/></div>
      </div>
      {/* Top 事件 */}
      <div style={{ marginBottom: 32 }}>
        <div className="skeleton" style={{ height: 14, width: 120, marginBottom: 16 }} />
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="skel-item">
            <div className="skeleton skel-title" />
            <div className="skeleton skel-meta" />
          </div>
        ))}
      </div>
      {/* Top 资讯 */}
      <div>
        <div className="skeleton" style={{ height: 14, width: 120, marginBottom: 16 }} />
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="skel-item">
            <div className="skeleton skel-title" />
            <div className="skeleton skel-meta" />
          </div>
        ))}
      </div>
    </div>
  )
}