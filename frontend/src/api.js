// 云函数 API 封装。开发默认用 mock 数据，生产走热铁盒云函数

const BASE = import.meta.env.VITE_API_BASE || ''

// 热铁盒路径映射: /api/v1/xxx → /xxx.node.js
function mapApiPath(p) {
  if (import.meta.env.DEV) return p
  return p
    .replace(/^\/api\/v1\/items/, '/items.node.js')
    .replace(/^\/api\/v1\/hot-topics/, '/hot-topics.node.js')
    .replace(/^\/api\/v1\/daily\/latest/, '/daily.node.js')
    .replace(/^\/api\/v1\/story\//, '/story.node.js?id=')
}

const USE_MOCK = import.meta.env.DEV

async function fetchJson(path) {
  if (USE_MOCK) {
    const { mockData } = await import('./mock.js')
    if (mockData[path]) return mockData[path]
    const [basePath, queryStr] = path.split('?')
    const wantMode = queryStr && queryStr.includes('mode=') ? queryStr.match(/mode=([^&]+)/)[1] : null
    let matchedKey
    if (wantMode) {
      matchedKey = Object.keys(mockData).find(k => {
        const [bp, q] = k.split('?')
        return bp === basePath && q && q.includes('mode=' + wantMode)
      })
    }
    if (!matchedKey) {
      matchedKey = Object.keys(mockData).find(k => k.split('?')[0] === basePath)
    }
    if (matchedKey) return mockData[matchedKey]
    return null
  }
  try {
    const mappedPath = mapApiPath(path)
    const resp = await fetch(BASE + mappedPath)
    if (!resp.ok) throw new Error('HTTP ' + resp.status)
    return await resp.json()
  } catch (e) {
    console.warn('API 调用失败 ' + mapApiPath(path) + ':', e.message)
    throw e
  }
}

export const api = {
  getItems: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return fetchJson('/api/v1/items?' + qs)
  },
  getHotTopics: () => fetchJson('/api/v1/hot-topics'),
  getStory: (id) => fetchJson('/api/v1/story/' + id),
  getDaily: (date) => {
    const qs = date ? '?date=' + date : ''
    return fetchJson('/api/v1/daily/latest' + qs)
  },
}