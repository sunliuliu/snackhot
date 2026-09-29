/*
  GET /api/v1/story/:id
  事件详情：聚合该事件下所有 ProcessedItem 成员

  路径参数通过 req.params.id 获取（热铁盒云函数路由匹配）
  或用 query 参数 ?id=xxx
*/
const db = new Database("snackhot");

function getEventId() {
  if (typeof req === 'undefined') return null;
  // 热铁盒云函数可能不支持 req.params，降级用 query
  return (req.params && req.params.id) || (req.query && req.query.id) || null;
}

async function main() {
  if (typeof req === 'undefined') {
    return document.write(JSON.stringify({ ok: false, error: 'not in rth env' }));
  }

  const eventId = getEventId();
  if (!eventId) {
    document.write(JSON.stringify({ ok: false, error: 'missing id param' }));
    return;
  }

  const eventRaw = await db.get(`event:${eventId}`);
  if (!eventRaw) {
    document.write(JSON.stringify({ ok: false, error: 'event not found' }));
    return;
  }

  const event = JSON.parse(eventRaw);

  // 拉所有成员 items
  const members = [];
  for (const itemId of (event.member_ids || [])) {
    const raw = await db.get(`item:${itemId}`);
    if (raw) {
      try { members.push(JSON.parse(raw)); } catch { /* skip */ }
    }
  }

  document.write(JSON.stringify({
    schemaVersion: 1,
    event,
    members: members.sort((a, b) => new Date(b.discovered_at) - new Date(a.discovered_at)),
    member_count: members.length,
  }));
}

main();