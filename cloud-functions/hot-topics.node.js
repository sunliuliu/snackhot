/* hot-topics.node.js - GET /hot-topics.node.js
 * KV 分片兼容: 优先读不分片单 key，读不到再查 meta 拉 chunk 合并
 */
const db = new Database("snackhot");

// 读一个可能分片的快照 (向后兼容)
async function readSnapshot(baseKey, arrayField) {
  // 策略 1: 先尝试不分片格式
  const directRaw = await db.get(baseKey);
  if (directRaw) {
    try {
      return JSON.parse(directRaw);
    } catch (e) { /* fallthrough */ }
  }

  // 策略 2: 尝试分片格式
  const metaRaw = await db.get(baseKey + '__meta');
  if (!metaRaw) return null;

  let meta;
  try { meta = JSON.parse(metaRaw); } catch { return null; }

  const totalChunks = meta.total_chunks || 0;
  if (totalChunks === 0) return null;

  const allEvents = [];
  let generatedAt = null;

  for (let i = 0; i < totalChunks; i++) {
    const chunkRaw = await db.get(baseKey + '__chunk' + i);
    if (chunkRaw) {
      try {
        const chunk = JSON.parse(chunkRaw);
        generatedAt = generatedAt || chunk.generated_at;
        allEvents.push.apply(allEvents, chunk[arrayField] || []);
      } catch (e) { /* skip */ }
    }
  }

  return {
    generated_at: generatedAt || meta.generated_at,
    count: allEvents.length,
    [arrayField]: allEvents,
  };
}

async function main() {
  if (typeof req === 'undefined') {
    return document.write(JSON.stringify({ ok: false, error: 'not in rth env' }));
  }

  const latestDate = await db.get('index__latest_date') || new Date().toISOString().slice(0, 10);
  const eventIds = JSON.parse(await db.get('index__event_ids') || '[]');

  // 兼容分片读取
  const parsed = await readSnapshot('events__' + latestDate, 'events');
  let events = parsed ? (parsed.events || []) : [];

  events.sort((a, b) => (b.hot_score || 0) - (a.hot_score || 0));

  document.write(JSON.stringify({
    schemaVersion: 2,
    data_date: latestDate,
    updated_at: new Date().toISOString(),
    count: events.length,
    hot_topics: events,
  }));
}

main();