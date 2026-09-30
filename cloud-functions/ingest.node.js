/* ingest.node.js - POST /ingest.node.js
 * KV 分片升级: 自动检测数据大小，超 55KB 自动切片为 key__chunk0, key__chunk1, ...
 * 向后兼容: 不分片时仍写单个 key，读取端优先读老格式
 */
const db = new Database("snackhot");

// ============ 分片配置 ============
const MAX_CHUNK_BYTES = 55 * 1024;   // 55KB，留 10KB 余量给热铁盒 65KB 上限
const DB_WRITE_SIZE_LIMIT = 65 * 1024; // 热铁盒 KV 单值硬上限（安全校验用）

// ============ 分片辅助函数 ============

// 把大数组按序列化后大小切片
function chunkArray(items, generatedAt, maxBytes) {
  if (!items || items.length === 0) {
    return [{ generated_at: generatedAt, count: 0, items: [] }];
  }

  const chunks = [];
  let current = [];

  for (const item of items) {
    const testArr = current.concat(item);
    const testObj = { generated_at: generatedAt, count: testArr.length, items: testArr };
    const testSize = JSON.stringify(testObj).length;

    if (testSize > maxBytes && current.length > 0) {
      // 当前块已满，推出去开新块
      chunks.push({ generated_at: generatedAt, count: current.length, items: current });
      current = [item];
    } else {
      current.push(item);
    }
  }
  if (current.length > 0) {
    chunks.push({ generated_at: generatedAt, count: current.length, items: current });
  }

  return chunks;
}

// 写一个可能分片的快照
// 返回 { keys: [写入的所有 key], chunks: chunk 数量, used_chunking: 是否启用了分片 }
async function writeSnapshot(baseKey, dataObj, arrayField) {
  const generatedAt = dataObj.generated_at;
  const dataStr = JSON.stringify(dataObj);

  // 不分片: 直接写单个 key (向后兼容老的读取端)
  if (dataStr.length <= MAX_CHUNK_BYTES) {
    await db.set(baseKey, dataStr);
    return { keys: [baseKey], chunks: 1, used_chunking: false };
  }

  // 分片写入
  const array = dataObj[arrayField] || [];
  const chunks = chunkArray(array, generatedAt, MAX_CHUNK_BYTES);
  const writtenKeys = [];

  for (let i = 0; i < chunks.length; i++) {
    const chunkKey = baseKey + '__chunk' + i;
    await db.set(chunkKey, JSON.stringify(chunks[i]));
    writtenKeys.push(chunkKey);
  }

  // 写 meta 索引 (让读取端知道分了几片)
  const metaKey = baseKey + '__meta';
  await db.set(metaKey, JSON.stringify({
    total_chunks: chunks.length,
    total_items: array.length,
    generated_at: generatedAt,
    schema_version: 2,
  }));
  writtenKeys.push(metaKey);

  return { keys: writtenKeys, chunks: chunks.length, used_chunking: true };
}

// ============ 主流程 ============
async function main() {
  if (typeof req === 'undefined') {
    return document.write(JSON.stringify({ ok: false, error: 'not in rth env' }));
  }

  // API key check
  const API_KEY = req.headers
    ? (req.headers['x-api-key'] || req.headers['X-API-Key'] || '')
    : '';
  const VALID_KEYS = [process.env.INGEST_API_KEY || 'snackhot-2025'];
  if (API_KEY && !VALID_KEYS.includes(API_KEY)) {
    return document.write(JSON.stringify({ ok: false, error: 'unauthorized' }));
  }

  // Rate limit
  const lastPush = await db.get('meta__last_push_ts');
  const now = Date.now();
  if (lastPush && now - parseInt(lastPush) < 15 * 60 * 1000) {
    return document.write(JSON.stringify({ ok: false, error: 'too frequent (< 15 min)' }));
  }

  // Parse body
  let payload;
  try {
    const raw = typeof req.body === 'string' ? req.body : JSON.stringify(req.body || {});
    payload = JSON.parse(raw);
  } catch (e) {
    return document.write(JSON.stringify({ ok: false, error: 'invalid json' }));
  }
  if (!payload || !Array.isArray(payload.items)) {
    return document.write(JSON.stringify({ ok: false, error: 'invalid payload' }));
  }

  const ts = new Date();
  const dateStr = ts.toISOString().slice(0, 10);
  const tsStr = ts.toISOString();
  const items = payload.items.slice(0, 200);
  const events = (payload.events || []).slice(0, 50);
  const hotEventIds = (payload.events || [])
    .sort((a, b) => (b.hot_score || 0) - (a.hot_score || 0))
    .slice(0, 20).map(e => e.id);

  // 预估原始 payload 大小 (用于日志)
  const rawItemsSize = JSON.stringify(items).length;
  const rawEventsSize = JSON.stringify(events).length;

  // ============ 批量写入 (自动分片) ============

  // 1. items 快照
  const itemsKey = 'items__' + dateStr;
  const itemsResult = await writeSnapshot(itemsKey, {
    generated_at: tsStr, count: items.length, items: items,
  }, 'items');

  // 2. events 快照
  const eventsKey = 'events__' + dateStr;
  const eventsResult = await writeSnapshot(eventsKey, {
    generated_at: tsStr, count: events.length, events: events,
  }, 'events');

  // 3. 索引 key (不分片)
  await db.set('index__latest_date', dateStr);
  await db.set('index__event_ids', JSON.stringify(hotEventIds));

  // 4. daily 早报 (不分片, 数据量很小)
  await db.set('daily__' + dateStr, JSON.stringify({
    date: dateStr, generated_at: tsStr,
    item_count: items.length, event_count: events.length,
    top_events: events.slice(0, 5).map(e => ({ title: e.title, score: e.hot_score })),
  }));
  await db.set('daily__latest', 'daily__' + dateStr);

  // 5. 限流追踪
  await db.set('meta__last_push_ts', String(Date.now()));
  await db.set('meta__total_pushes', String(parseInt(await db.get('meta__total_pushes') || '0') + 1));

  // ============ 返回 ============
  const totalKvOps = itemsResult.keys.length + eventsResult.keys.length + 5;

  document.write(JSON.stringify({
    ok: true,
    written: {
      items_key: itemsResult.used_chunking ? itemsKey + ' (' + itemsResult.chunks + ' chunks)' : itemsKey,
      events_key: eventsResult.used_chunking ? eventsKey + ' (' + eventsResult.chunks + ' chunks)' : eventsKey,
      item_count: items.length,
      event_count: events.length,
      kv_operations: totalKvOps,
      items_chunked: itemsResult.used_chunking,
      events_chunked: eventsResult.used_chunking,
      items_size_kb: (rawItemsSize / 1024).toFixed(1),
      events_size_kb: (rawEventsSize / 1024).toFixed(1),
    },
    timestamp: tsStr,
  }));
}

main();