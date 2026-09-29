/* hot-topics.node.js - GET /hot-topics.node.js */
const db = new Database("snackhot");

async function main() {
  if (typeof req === 'undefined') {
    return document.write(JSON.stringify({ ok: false, error: 'not in rth env' }));
  }
  const latestDate = await db.get('index__latest_date') || new Date().toISOString().slice(0, 10);
  const eventIds = JSON.parse(await db.get('index__event_ids') || '[]');
  const eventsRaw = await db.get('events__' + latestDate);

  let events = [];
  if (eventsRaw) {
    const parsed = JSON.parse(eventsRaw);
    events = parsed.events || [];
  }
  events.sort((a, b) => (b.hot_score || 0) - (a.hot_score || 0));

  document.write(JSON.stringify({ schemaVersion: 2, data_date: latestDate, count: events.length, hot_topics: events }));
}

main();