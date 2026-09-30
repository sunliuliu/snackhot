/* brands.node.js - GET /brands.node.js
 * 返回零食连锁品牌榜单 + 今日涉及各品牌的资讯数
 * 支持 tier=1/2/3 参数筛选
 */
const db = new Database("snackhot");

// 品牌词库 (和爬虫 config.py 同步维护)
const BRAND_KEYWORDS = [
  // Tier 1 - 全国龙头
  "鸣鸣很忙","零食很忙","赵一鸣","好想来","老婆大人","来优品","吖嘀吖嘀","陆小馋","万辰集团",
  "良品铺子","三只松鼠","来伊份","薛记炒货",
  "旺旺","卫龙","盐津铺子","绝味","洽洽","亿滋","玛氏","雀巢","好时","百事","可口可乐",
  "农夫山泉","元气森林","伊利","蒙牛","光明","娃哈哈","康师傅","统一",
  "双汇","安井","三全","思念","劲仔","麻辣王子","甘源",
  "喜茶","奈雪的茶","茶颜悦色","霸王茶姬","蜜雪冰城","古茗","一点点","CoCo",
  
  // Tier 2 - 区域领导
  "零食有鸣","糖巢","零食优选","爱零食","戴永红",
  
  // Tier 3 - 地方品牌
  "零食舱","桔子花开","零食顽家","零食青蛙","金粒门","几多全","一栗",
  
  // 制造巨头
  "奥利奥","大白兔","徐福记","达利园","盼盼","好丽友","金丝猴","马大姐",
];

// 门店规模数据 (静态维护)
const BRAND_STATS = {
  "鸣鸣很忙": { stores: "30000+",  region: "全国",          gmv: "936亿",  desc: "量贩零食第一股" },
  "零食很忙": { stores: "合并入鸣鸣", region: "湖南起家",    gmv: "-",      desc: "2017年长沙首店" },
  "赵一鸣":   { stores: "合并入鸣鸣", region: "江西宜春",    gmv: "-",      desc: "2019年首店" },
  "好想来":   { stores: "19500+",  region: "长三角+华北",   gmv: "733亿",  desc: "万辰集团旗下" },
  "老婆大人": { stores: "并入好想来", region: "华东",         gmv: "-",      desc: "最早量贩品牌" },
  "零食有鸣": { stores: "6000+",   region: "四川/西南",     gmv: "-",      desc: "西南龙头" },
  "糖巢":     { stores: "1500+",   region: "福建/华东",     gmv: "-",      desc: "福建起家" },
  "良品铺子": { stores: "3000+",   region: "全国",          gmv: "-",      desc: "传统连锁头部" },
  "三只松鼠": { stores: "1000+",   region: "全国",          gmv: "-",      desc: "线上起家" },
  "来伊份":   { stores: "3000+",   region: "华东",          gmv: "-",      desc: "江浙沪起家" },
  "薛记炒货": { stores: "1000+",   region: "全国",          gmv: "-",      desc: "高端炒货" },
  "爱零食":   { stores: "1000+",   region: "湖南",          gmv: "-",      desc: "湖南特色" },
  "零食优选": { stores: "1500+",   region: "湖南",          gmv: "-",      desc: "湖南龙头" },
  "戴永红":   { stores: "200+",    region: "湖南",          gmv: "-",      desc: "湖南老牌" },
};

async function main() {
  if (typeof req === 'undefined') {
    return document.write(JSON.stringify({ ok: false, error: 'not in rth env' }));
  }

  const latestDate = await db.get('index__latest_date') || new Date().toISOString().slice(0, 10);
  
  // 读 items (分片兼容)
  let itemsRaw = await db.get('items__' + latestDate);
  if (!itemsRaw) {
    const meta = await db.get('items__' + latestDate + '__meta');
    if (meta) {
      let all = [];
      const m = JSON.parse(meta);
      for (let i = 0; i < m.total_chunks; i++) {
        const chunk = await db.get('items__' + latestDate + '__chunk' + i);
        if (chunk) { all = all.concat(JSON.parse(chunk)); }
      }
      itemsRaw = JSON.stringify({ items: all });
    }
  }
  
  let items = [];
  try { items = JSON.parse(itemsRaw).items || []; } catch {}
  
  // 统计每个品牌出现次数
  const brandCount = {};
  items.forEach(item => {
    const text = (item.title + ' ' + (item.summary || '')).toLowerCase();
    BRAND_KEYWORDS.forEach(bk => {
      if (text.includes(bk.toLowerCase())) {
        brandCount[bk] = (brandCount[bk] || 0) + 1;
      }
    });
  });
  
  // 排序输出
  const ranked = Object.entries(brandCount)
    .map(([brand, count]) => ({ 
      brand, count, 
      stats: BRAND_STATS[brand] || { stores: "-", region: "-", gmv: "-", desc: "待补充" }
    }))
    .sort((a, b) => b.count - a.count);
  
  document.write(JSON.stringify({
    schemaVersion: 2,
    data_date: latestDate,
    updated_at: new Date().toISOString(),
    total_brands: ranked.length,
    ranked_brands: ranked,
  }));
}

main();
