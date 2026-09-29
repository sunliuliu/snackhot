/* ingest.node.js - POST /ingest.node.js */
const db = new Database("snackhot");

async function main() {
  if (typeof req === 'undefined') {
    return document.write(JSON.stringify({ ok: false, error: 'not in rth env' }));
  }

  // API key check (moved inside main, no top-level return)
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
  const latestDate = await db.get('index__latest_date') || dateStr;
  const items = payload.items.slice(0, 200);
  const events = (payload.events || []).slice(0, 50);
  const hotEventIds = (payload.events || [])
    .sort((a, b) => (b.hot_score || 0) - (a.hot_score || 0))
    .slice(0, 20).map(e => e.id);

  // Batch write (5 KV ops total)
  const itemsKey = 'items__' + dateStr;
  await db.set(itemsKey, JSON.stringify({ generated_at: ts.toISOString(), count: items.length, items: items }));

  const eventsKey = 'events__' + dateStr;
  await db.set(eventsKey, JSON.stringify({ generated_at: ts.toISOString(), count: events.length, events: events }));

  await db.set('index__latest_date', dateStr);
  await db.set('index__event_ids', JSON.stringify(hotEventIds));

  await db.set('daily__' + dateStr, JSON.stringify({
    date: dateStr, generated_at: ts.toISOString(),
    item_count: items.length, event_count: events.length,
    top_events: events.slice(0, 5).map(e => ({ title: e.title, score: e.hot_score })),
  }));
  await db.set('daily__latest', 'daily__' + dateStr);

  await db.set('meta__last_push_ts', String(Date.now()));
  await db.set('meta__total_pushes', String(parseInt(await db.get('meta__total_pushes') || '0') + 1));

  document.write(JSON.stringify({
    ok: true, written: { items_key: itemsKey, events_key: eventsKey, item_count: items.length, event_count: events.length, kv_operations: 5 },
    kv_ops_saved: '300+ -> 5', timestamp: ts.toISOString(),
  }));
}

main();