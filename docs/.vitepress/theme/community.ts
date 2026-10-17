import { withBase } from 'vitepress'
export const websiteId = 'fa4e9f07-6328-46d1-ad63-16ab7ec3682a'
export const shareSlug = 'jfred-public'
export const communityEnabled = () => typeof window !== 'undefined' && !import.meta.env.DEV && !['localhost','127.0.0.1'].includes(window.location.hostname) && !window.location.hostname.endsWith('github.io')
export const canonicalPath = (path: string) => path.split(/[?#]/)[0].replace(/\.html$/, '').replace(/\/$/, '') || '/'
let tokenRequest: Promise<string> | undefined
const cache = new Map<string, { expires: number; value: Promise<{ pageviews: number; visitors: number }> }>()
async function publicToken() {
  if (!tokenRequest) tokenRequest = fetch(withBase(`/metrics/api/share/${shareSlug}`)).then(async r => {
    if (!r.ok) throw new Error('统计服务暂不可用')
    return (await r.json()).token as string
  }).catch(e => { tokenRequest = undefined; throw e })
  return tokenRequest
}
export function getPublicStats(path?: string, startAt = 1791129600000, endAt = Date.now()) {
  const key = `${path || '*'}:${startAt}:${Math.floor(endAt / 30000)}`
  const previous = cache.get(key)
  if (previous && previous.expires > Date.now()) return previous.value
  const value = (async () => {
    if (!communityEnabled()) throw new Error('统计仅在服务器站点启用')
    const token = await publicToken()
    const params = new URLSearchParams({ startAt: String(startAt), endAt: String(endAt), timezone: 'Asia/Shanghai' })
    if (path) params.set('path', canonicalPath(path))
    const response = await fetch(withBase(`/metrics/api/websites/${websiteId}/stats?${params}`), { headers: { 'x-umami-share-token': token, 'x-umami-share-context': 'website' } })
    if (!response.ok) throw new Error('统计服务暂不可用')
    const result = await response.json()
    return { pageviews: Number(result.pageviews), visitors: Number(result.visitors) }
  })()
  cache.set(key, { expires: Date.now() + 30000, value })
  value.catch(() => cache.delete(key))
  return value
}
