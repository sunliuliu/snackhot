/* items.node.js - GET /items.node.js */
const db = new Database("snackhot");

function getQuery(name, def = '') {
  if (typeof req === 'undefined') return def;
  const q = req.query || {};
  return q[name] !== undefined ? q[name] : def;
}

async function main() {
  if (typeof req === 'undefined') {
    return document.write(JSON.stringify({ ok: false, error: 'not in rth env' }));
  }
  const mode = getQuery('mode', 'selected');
  const category = getQuery('category', '');
  const limit = Math.min(parseInt(getQuery('limit', '20')) || 20, 30);

  const latestDate = await db.get('index__latest_date') || new Date().toISOString().slice(0, 10);
  const itemsRaw = await db.get('items__' + latestDate);

  let items = [];
  if (itemsRaw) {
    const parsed = JSON.parse(itemsRaw);
    items = parsed.items || [];
  }
  if (category) items = items.filter(i => i.category === category);
  if (mode === 'selected') items = items.filter(i => i.selected);
  items.sort((a, b) => new Date(b.discovered_at || 0) - new Date(a.discovered_at || 0));
  items = items.slice(0, limit);

  document.write(JSON.stringify({ schemaVersion: 2, data_date: latestDate, count: items.length, items: items }));
}

main();