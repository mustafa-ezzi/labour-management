/** Remember last-opened site for shortcuts, resume links, and legacy URL redirects. */

export const LAST_SITE_KEY = 'lm:lastSiteId'

export const LAST_SITE_COOKIE_NAME = 'lm-last-site-id'

export const lastSiteCookieOpts = {
  path: '/' as const,
  maxAge: 60 * 60 * 24 * 365,
  sameSite: 'lax' as const,
}

export function persistSiteId(siteId: string) {
  if (import.meta.client) {
    localStorage.setItem(LAST_SITE_KEY, siteId)
  }
  const cookie = useCookie<string | null>(LAST_SITE_COOKIE_NAME, lastSiteCookieOpts)
  cookie.value = siteId
}

/** Prefers localStorage on client (more up-to-date), then cookie (SSR + hydrated client). */
export function readResolvedLastSiteId(cookieValue: string | null | undefined): string | null {
  if (import.meta.client) {
    const ls = localStorage.getItem(LAST_SITE_KEY)
    if (ls) return ls
  }
  return cookieValue ?? null
}

/** Call from setup — returns `/sites/:id` or null. */
export function useResumeSitePath() {
  const cookie = useCookie<string | null>(LAST_SITE_COOKIE_NAME, lastSiteCookieOpts)
  return computed(() => {
    const id = readResolvedLastSiteId(cookie.value)
    return id ? `/sites/${id}` : null
  })
}
