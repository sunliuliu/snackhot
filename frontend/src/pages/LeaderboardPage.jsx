import { useState } from 'react'

// ========== 三类排行榜 ==========

// 1. 零售连锁热度榜（好想来、零食很忙、赵一鸣这类 —— 用户要的重点）
const RETAIL_RANK = [
  { rank:1, name:'好想来',        score: 962, delta:'+18', cat:'零食量贩连锁',  storeCount:'>5000 家门店',   highlight:'零食量贩头部，下沉市场称王，2026 门店突破 5000 家' },
  { rank:2, name:'零食很忙',      score: 848, delta:'+24', cat:'零食量贩连锁',  storeCount:'3200+ 家门店',  highlight:'华中地区扩张最快，完成 D 轮 10 亿融资' },
  { rank:3, name:'赵一鸣零食',    score: 786, delta:'+31', cat:'零食量贩连锁',  storeCount:'2800+ 家门店',  highlight:'反超零食很忙成为江西第一，抖音话题量破 20 亿' },
  { rank:4, name:'零食代',        score: 624, delta:'+12', cat:'零食量贩连锁',  storeCount:'1800+ 家门店',  highlight:'山东市场龙头，北方扩张加速' },
  { rank:5, name:'贪吃嘴',        score: 538, delta:'+8',  cat:'零食量贩连锁',  storeCount:'1500+ 家门店',  highlight:'福建起家，东南沿海布局' },
  { rank:6, name:'怡佳仁',        score: 472, delta:'-3',  cat:'零食量贩连锁',  storeCount:'1200+ 家门店',  highlight:'老牌连锁，数字化转型中' },
  { rank:7, name:'良品铺子',      score: 426, delta:'+5',  cat:'高端零食连锁',  storeCount:'3800+ 家门店',  highlight:'新鲜 7.0 门店模型迭代，往线下便利店走' },
  { rank:8, name:'来伊份',        score: 385, delta:'-2',  cat:'高端零食连锁',  storeCount:'2200+ 家门店',  highlight:'上海起家，高端路线承压' },
  { rank:9, name:'老婆大人',      score: 312, delta:'+6',  cat:'零食量贩连锁',  storeCount:'900+ 家门店',   highlight:'浙江老牌，被好来想收购整合中' },
  { rank:10,name:'零零嘴',        score: 268, delta:'+15', cat:'零食量贩连锁',  storeCount:'500+ 家门店',   highlight:'新势力，主打社区 + 低价' },
]

// 2. 上游品牌热度榜（三只松鼠、卫龙等生产方 —— 不是零售商）
const BRAND_RANK = [
  { rank:1, name:'三只松鼠',   score: 892, delta:'+12', cat:'坚果炒货',  highlight:'半年报净利 +79.94%，高端性价比模型验证成功' },
  { rank:2, name:'卫龙',       score: 756, delta:'-5',  cat:'肉脯卤味',  highlight:'魔芋爽增速从 100%+ 骤降至 15%' },
  { rank:3, name:'洽洽食品',   score: 638, delta:'+22', cat:'坚果炒货',  highlight:'投建云南曲靖魔芋智能工厂，抢上游原料' },
  { rank:4, name:'盐津铺子',   score: 572, delta:'+3',  cat:'肉脯卤味',  highlight:'魔芋零食高增长时代落幕' },
  { rank:5, name:'奥利奥',     score: 438, delta:'+26', cat:'饼干糕点',  highlight:'联名肯德基推出限量甜品套餐' },
  { rank:6, name:'百草味',     score: 385, delta:'+1',  cat:'坚果炒货',  highlight:'新品系列推出中' },
  { rank:7, name:'旺旺',       score: 326, delta:'-2',  cat:'膨化食品',  highlight:'秋季新品即将发布' },
  { rank:8, name:'好丽友',     score: 297, delta:'+9',  cat:'饼干糕点',  highlight:'新品上市' },
]

// 3. 电商渠道热度榜
const CHANNEL_RANK = [
  { rank:1, name:'抖音电商',   score: 924, delta:'+28', highlight:'零食自播 + 达人矩阵双驱动，2026 GMV 破千亿' },
  { rank:2, name:'天猫超市',   score: 756, delta:'+8',  highlight:'每日鲜 + 小时达，线上零食第一入口' },
  { rank:3, name:'京东到家',   score: 628, delta:'+15', highlight:'即时零售崛起，30 分钟达' },
  { rank:4, name:'拼多多',     score: 584, delta:'+12', highlight:'百亿补贴 + 多多买菜，下沉市场拉满' },
  { rank:5, name:'美团闪购',   score: 412, delta:'+35', highlight:'零食外卖年增长超 200%' },
  { rank:6, name:'视频号',     score: 326, delta:'+42', highlight:'品牌私域直播新入口' },
]

// 4. 爆款单品榜
const HOT_PRODUCTS = [
  { rank:1, name:'卫龙魔芋爽（酸辣味）',     cat:'肉脯卤味',     brand:'卫龙',      price:'¥19.9/袋',  highlight:'连续 12 个月抖音零食热销 Top 1' },
  { rank:2, name:'恰恰每日坚果',             cat:'坚果炒货',     brand:'洽洽食品',   price:'¥29.9/盒',  highlight:'超 10 亿袋销量，国民坚果' },
  { rank:3, name:'三只松鼠纸皮核桃',         cat:'坚果炒货',     brand:'三只松鼠',   price:'¥49.9/500g',highlight:'半年爆卖 2.3 亿袋' },
  { rank:4, name:'良品铺子每日坚果',         cat:'坚果炒货',     brand:'良品铺子',   price:'¥39.9/盒',  highlight:'线下渠道 + 线上双爆' },
  { rank:5, name:'王小卤虎皮凤爪',           cat:'肉脯卤味',     brand:'王小卤',     price:'¥29.9/200g',highlight:'网红卤味代表' },
  { rank:6, name:'奥利奥原味饼干',           cat:'饼干糕点',     brand:'奥利奥',     price:'¥15.9/包',  highlight:'百年经典，联名不断' },
  { rank:7, name:'乐事黄瓜味薯片',           cat:'膨化食品',     brand:'乐事',       price:'¥9.9/袋',   highlight:'夏季爆品' },
  { rank:8, name:'百草味每日坚果',           cat:'坚果炒货',     brand:'百草味',     price:'¥25.9/盒',  highlight:'性价比路线' },
]

const TABS = [
  { key:'retail',  label:'零售连锁榜' },
  { key:'brand',   label:'品牌热度榜' },
  { key:'channel', label:'电商渠道榜' },
  { key:'product', label:'爆款单品榜' },
]

export default function LeaderboardPage() {
  const [tab, setTab] = useState('retail')

  return (
    <div>
      <h1 className="page-title">🏆 零食行业排行榜</h1>
      <p className="page-sub">数据综合 AI 热度指数、媒体报道、社交提及量自动生成 · 每 6 小时更新</p>

      <div className="flex gap-1 mb-6 flex-wrap">
        {TABS.map(t => (
          <button key={t.key} onClick={()=>setTab(t.key)}
            className={`px-3 py-1.5 text-[13px] transition-colors border ${
              tab === t.key
                ? 'bg-[rgb(32,42,48)] text-white border-[rgb(32,42,48)] font-medium'
                : 'text-[rgb(130,140,145)] border-[rgb(223,228,225)] hover:border-[rgb(130,140,145)] hover:text-[rgb(32,42,48)]'
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'retail'  && <RetailRank />}
      {tab === 'brand'   && <BrandRank />}
      {tab === 'channel' && <ChannelRank />}
      {tab === 'product' && <ProductRank />}
    </div>
  )
}

// ============ 零售连锁榜 ============
function RetailRank() {
  const maxScore = Math.max(...RETAIL_RANK.map(b => b.score))
  return (
    <div className="space-y-0">
      {RETAIL_RANK.map(b => (
        <div key={b.rank} className="grid grid-cols-[40px_1fr_100px_90px] gap-3 items-center py-4 border-b border-[rgb(223,228,225)] last:border-b-0 hover:bg-[rgb(249,249,246)] transition-colors">
          {/* 排名 */}
          <div className={`font-mono font-bold leading-none ${
            b.rank === 1 ? 'text-[28px] text-amber-500' :
            b.rank === 2 ? 'text-[22px] text-gray-400' :
            b.rank === 3 ? 'text-[18px] text-orange-400' :
            'text-[14px] text-[rgb(130,140,145)]'
          }`}>#{b.rank}</div>

          {/* 主体：名称 + 业态 + 门店数 + 亮点 */}
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[15px] font-semibold text-[rgb(32,42,48)]">{b.name}</span>
              <span className="text-[11px] px-1.5 py-0.5 bg-[rgb(243,243,239)] text-[rgb(89,101,107)] rounded-full">{b.cat}</span>
              <span className="text-[11px] text-[rgb(130,140,145)] font-mono">🏪 {b.storeCount}</span>
            </div>
            <div className="text-[12px] text-[rgb(89,101,107)] mt-1">{b.highlight}</div>
          </div>

          {/* 热度指数 + 可视化条 */}
          <div>
            <div className="text-right font-mono font-semibold text-[15px] text-[rgb(48,60,66)] tabular-nums">{b.score}</div>
            <div className="mt-1 h-[4px] bg-[rgb(223,228,225)] relative max-w-[100px] ml-auto">
              <div className="absolute inset-y-0 right-0 bg-[rgb(32,42,48)]" style={{ width: `${(b.score / maxScore) * 100}%` }}></div>
            </div>
          </div>

          {/* 趋势 */}
          <div className="text-right">
            <span className={`font-mono text-[13px] font-bold tabular-nums ${
              b.delta.startsWith('-') ? 'text-[rgb(22,135,85)]' : 'text-[rgb(22,135,85)]'
            }`}>{b.delta}</span>
          </div>
        </div>
      ))}
    </div>
  )
}

// ============ 品牌热度榜（上游生产方） ============
function BrandRank() {
  const maxScore = Math.max(...BRAND_RANK.map(b => b.score))
  return (
    <div className="space-y-0">
      {BRAND_RANK.map(b => (
        <div key={b.rank} className="grid grid-cols-[40px_1fr_80px_80px] gap-3 items-center py-3 border-b border-[rgb(223,228,225)] last:border-b-0 hover:bg-[rgb(249,249,246)]">
          <div className={`font-mono font-bold leading-none ${
            b.rank === 1 ? 'text-[26px] text-amber-500' :
            b.rank === 2 ? 'text-[20px] text-gray-400' :
            b.rank === 3 ? 'text-[17px] text-orange-400' :
            'text-[14px] text-[rgb(130,140,145)]'
          }`}>#{b.rank}</div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-[14px] font-semibold text-[rgb(32,42,48)]">{b.name}</span>
              <span className="text-[11px] px-1.5 py-0.5 bg-[rgb(243,243,239)] text-[rgb(89,101,107)] rounded-full">{b.cat}</span>
            </div>
            <div className="text-[12px] text-[rgb(130,140,145)] mt-0.5 truncate">{b.highlight}</div>
          </div>
          <div className="text-right">
            <div className="font-mono font-semibold text-[15px] text-[rgb(48,60,66)] tabular-nums">{b.score}</div>
            <div className="mt-1 h-[4px] bg-[rgb(223,228,225)] relative max-w-[80px] ml-auto">
              <div className="absolute inset-y-0 right-0 bg-[rgb(32,42,48)]" style={{ width: `${(b.score / maxScore) * 100}%` }}></div>
            </div>
          </div>
          <div className="text-right">
            <span className="font-mono text-[13px] font-bold tabular-nums text-[rgb(22,135,85)]">{b.delta}</span>
          </div>
        </div>
      ))}
    </div>
  )
}

// ============ 电商渠道榜 ============
function ChannelRank() {
  const maxScore = Math.max(...CHANNEL_RANK.map(s => s.score))
  return (
    <div className="space-y-0">
      {CHANNEL_RANK.map((s, i) => (
        <div key={s.name} className="grid grid-cols-[40px_1fr_80px_100px] gap-3 items-center py-3 border-b border-[rgb(223,228,225)] last:border-b-0 hover:bg-[rgb(249,249,246)]">
          <div className="font-mono font-bold text-[14px] text-[rgb(130,140,145)]">#{i+1}</div>
          <div className="min-w-0">
            <div className="text-[14px] font-semibold text-[rgb(32,42,48)]">{s.name}</div>
            <div className="text-[12px] text-[rgb(130,140,145)] mt-0.5">{s.highlight}</div>
          </div>
          <div className="font-mono font-semibold text-[13px] text-right text-[rgb(48,60,66)]">{s.score}</div>
          <div className="h-[4px] bg-[rgb(223,228,225)] relative">
            <div className="absolute inset-y-0 left-0 bg-[rgb(32,42,48)]" style={{ width: `${(s.score/maxScore)*100}%` }}></div>
          </div>
        </div>
      ))}
    </div>
  )
}

// ============ 爆款单品榜 ============
function ProductRank() {
  return (
    <div className="grid sm:grid-cols-2 gap-4">
      {HOT_PRODUCTS.map(p => (
        <div key={p.rank} className="border border-[rgb(223,228,225)] bg-white p-4 hover:shadow-sm transition-shadow">
          <div className="flex items-start gap-3">
            <span className={`font-mono font-bold leading-none shrink-0 ${
              p.rank === 1 ? 'text-[22px] text-amber-500' :
              p.rank === 2 ? 'text-[18px] text-gray-400' :
              p.rank === 3 ? 'text-[15px] text-orange-400' :
              'text-[13px] text-[rgb(130,140,145)]'
            }`}>#{p.rank}</span>
            <div className="min-w-0 flex-1">
              <div className="text-[14px] font-semibold text-[rgb(32,42,48)]">{p.name}</div>
              <div className="mt-1 flex items-center gap-2 text-[11px] text-[rgb(130,140,145)]">
                <span>{p.brand}</span>
                <span>·</span>
                <span>{p.cat}</span>
                <span className="ml-auto font-mono text-[12px] text-[rgb(180,83,9)]">{p.price}</span>
              </div>
              <div className="mt-2 text-[12px] text-[rgb(89,101,107)]">{p.highlight}</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}