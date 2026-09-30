/* items.node.js - GET /items.node.js
 * KV 分片兼容: 优先读不分片单 key，读不到再查 meta 拉 chunk 合并
 */
const db = new Database("snackhot");

function getQuery(name, def = '') {
  if (typeof req === 'undefined') return def;
  const q = req.query || {};
  return q[name] !== undefined ? q[name] : def;
}

// 读一个可能分片的快照 (向后兼容)
async function readSnapshot(baseKey, arrayField) {
  // 策略 1: 先尝试不分片格式 (老格式 / 不超阈值的新格式)
  const directRaw = await db.get(baseKey);
  if (directRaw) {
    try {
      return JSON.parse(directRaw);
    } catch (e) { /* fallthrough to chunked path */ }
  }

  // 策略 2: 尝试分片格式
  const metaRaw = await db.get(baseKey + '__meta');
  if (!metaRaw) {
    return null; // 老数据也没有，说明今天没推过
  }

  let meta;
  try { meta = JSON.parse(metaRaw); } catch { return null; }

  const totalChunks = meta.total_chunks || 0;
  if (totalChunks === 0) return null;

  // 逐个拉 chunk 合并
  const allItems = [];
  let generatedAt = null;
  let chunkCount = 0;

  for (let i = 0; i < totalChunks; i++) {
    const chunkRaw = await db.get(baseKey + '__chunk' + i);
    if (chunkRaw) {
      try {
        const chunk = JSON.parse(chunkRaw);
        generatedAt = generatedAt || chunk.generated_at;
        allItems.push.apply(allItems, chunk[arrayField] || []);
        chunkCount++;
      } catch (e) { /* skip bad chunk */ }
    }
  }

  return {
    generated_at: generatedAt || meta.generated_at,
    count: allItems.length,
    [arrayField]: allItems,
    _merged_from_chunks: chunkCount,
  };
}

async function main() {
  if (typeof req === 'undefined') {
    return document.write(JSON.stringify({ ok: false, error: 'not in rth env' }));
  }

  const mode = getQuery('mode', 'selected');
  const category = getQuery('category', '');
  const limit = Math.min(parseInt(getQuery('limit', '20')) || 20, 30);

  const latestDate = await db.get('index__latest_date') || new Date().toISOString().slice(0, 10);

  // 兼容分片读取
  const parsed = await readSnapshot('items__' + latestDate, 'items');
  let items = parsed ? (parsed.items || []) : [];

  // 筛选
  if (category) items = items.filter(i => i.category === category);
  if (mode === 'selected') items = items.filter(i => i.selected);

  items.sort((a, b) => new Date(b.discovered_at || 0) - new Date(a.discovered_at || 0));
  items = items.slice(0, limit);

  const resp = { schemaVersion: 2, data_date: latestDate, count: items.length, items: items };
  if (parsed && parsed._merged_from_chunks) {
    resp._chunks_merged = parsed._merged_from_chunks;
  }

  document.write(JSON.stringify(resp));
}

main();