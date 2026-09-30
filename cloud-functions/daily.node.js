/*
  GET /api/v1/daily/latest
  获取最新每日早报。可传 ?date=YYYY-MM-DD 获取指定日期。
  修复: KV key 统一用双下划线 __ (热铁盒不支持冒号)
*/
const db = new Database("snackhot");

async function main() {
  if (typeof req === 'undefined') {
    return document.write(JSON.stringify({ ok: false, error: 'not in rth env' }));
  }

  const query = req.query || {};
  let dateKey;

  if (query.date) {
    // 用户指定了日期
    dateKey = 'daily__' + query.date;
  } else {
    // 读最新索引
    const latest = await db.get('daily__latest');
    dateKey = latest || ('daily__' + new Date().toISOString().slice(0, 10));
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