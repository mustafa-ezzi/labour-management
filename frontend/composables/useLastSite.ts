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

export function clearLastSiteId() {
  if (import.meta.client) {
    localStorage.removeItem(LAST_SITE_KEY)
  }
  const cookie = useCookie<string | null>(LAST_SITE_COOKIE_NAME, lastSiteCookieOpts)
  cookie.value = null
}

/** Prefers localStorage on client (more up-to-date), then cookie (SSR + hydrated client). */
export function readResolvedLastSiteId(cookieValue: string | null | undefined): string | null {
  if (import.meta.client) {
    const ls = localStorage.getItem(LAST_SITE_KEY)
    if (ls) return ls
  }
  return cookieValue ?? null
}

/**
 * Resume link only when the stored site still exists for this user.
 * New accounts / empty workspaces never show “Resume last opened site”.
 */
export function useResumeSitePath() {
  const api = createApiClient()
  const cookie = useCookie<string | null>(LAST_SITE_COOKIE_NAME, lastSiteCookieOpts)
  const path = ref<string | null>(null)

  async function resolve() {
    const id = readResolvedLastSiteId(cookie.value)
    if (!id) {
      path.value = null
      return
    }
    try {
      await api.get(`/sites/${id}/`)
      path.value = `/sites/${id}`
    } catch {
      clearLastSiteId()
      path.value = null
    }
  }

  onMounted(() => {
    resolve()
  })

  return computed(() => path.value)
}
