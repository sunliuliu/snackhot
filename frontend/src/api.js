// 云函数 API 封装
// 生产请求热铁盒 .node.js 文件, 开发默认 mock
const BASE = import.meta.env.VITE_API_BASE || ''
const envOverride = import.meta.env.VITE_USE_MOCK
const USE_MOCK = envOverride !== undefined
  ? envOverride === 'true'
  : import.meta.env.DEV

async function fetchJson(path) {
  if (USE_MOCK) {
    try {
      const { mockData } = await import('./mock.js')
      if (mockData[path]) return mockData[path]
      const altKey = path.replace(/^/, '/api/v1')
      if (mockData[altKey]) return mockData[altKey]
      return null
    } catch(e) { return null }
  }
  try {
    const resp = await fetch(BASE + path)
    if (!resp.ok) throw new Error('HTTP ' + resp.status)
    return await resp.json()
  } catch (e) {
    console.warn('API fail ' + path + ':', e.message)
    throw e
  }
}

export const api = {
  getItems: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return fetchJson('/items.node.js?' + qs)
  },
  getHotTopics: () => fetchJson('/hot-topics.node.js'),
  getStory: (id) => fetchJson('/story.node.js?id=' + id),
  getDaily: (date) => {
    const qs = date ? '?date=' + date : ''
    return fetchJson('/daily.node.js' + qs)
  },
}
