/*
  GET /api/v1/daily/latest
  获取最新每日早报。可传 ?date=YYYY-MM-DD 获取指定日期。
*/
const db = new Database("snackhot");

async function main() {
  if (typeof req === 'undefined') {
    return document.write(JSON.stringify({ ok: false, error: 'not in rth env' }));
  }

  const query = req.query || {};
  let dateKey = query.date ? `daily:${query.date}` : null;

  if (!dateKey) {
    const latest = await db.get('daily__latest');
    dateKey = latest || `daily:${new Date().toISOString().slice(0, 10)}`;
  }

  const dailyRaw = await db.get(dateKey);
  if (!dailyRaw) {
    document.write(JSON.stringify({ ok: false, date: dateKey, error: 'not generated yet' }));
    return;
  }

  const daily = JSON.parse(dailyRaw);

  document.write(JSON.stringify({
    schemaVersion: 1,
    daily,
  }));
}

main();