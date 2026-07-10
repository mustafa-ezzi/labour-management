/**
 * Old URLs (/labour/*, /materials/*) → site-scoped routes.
 * Uses lm:lastSiteId / cookie when the URL did not include a site.
 */
import {
  LAST_SITE_COOKIE_NAME,
  lastSiteCookieOpts,
  readResolvedLastSiteId,
} from '~/composables/useLastSite'

export default defineNuxtRouteMiddleware((to) => {
  const cookie = useCookie<string | null>(LAST_SITE_COOKIE_NAME, lastSiteCookieOpts)
  const last = readResolvedLastSiteId(cookie.value) ?? ''
  const goSites = () => navigateTo('/sites')

  // ── Crew (was /labour) ─────────────────────────────────
  if (to.path === '/labour' || to.path === '/labour/') {
    return last ? navigateTo(`/sites/${last}/crew`) : goSites()
  }
  if (to.path === '/labour/attendance' || to.path === '/labour/pay') {
    return last ? navigateTo({ path: `/sites/${last}/crew/wages`, query: to.query }) : goSites()
  }
  if (to.path === '/labour/new') {
    return last ? navigateTo(`/sites/${last}/crew/new`) : goSites()
  }

  const payhist = to.path.match(/^\/labour\/([^/]+)\/payments\/?$/)
  if (payhist) {
    return last ? navigateTo(`/sites/${last}/crew/${payhist[1]}/payments`) : goSites()
  }

  const worker = to.path.match(/^\/labour\/([^/]+)\/?$/)
  if (worker) {
    const seg = worker[1]
    if (['pay', 'attendance', 'new'].includes(seg)) {
      return
    }
    return last ? navigateTo(`/sites/${last}/crew/${seg}`) : goSites()
  }

  // ── Materials ────────────────────────────────────────────
  if (to.path === '/materials' || to.path === '/materials/') {
    return last ? navigateTo(`/sites/${last}/materials`) : goSites()
  }
  if (to.path === '/materials/usage' || to.path === '/materials/usage/') {
    return last ? navigateTo({ path: `/sites/${last}/materials/usage`, query: to.query }) : goSites()
  }
  if (to.path === '/materials/new' || to.path === '/materials/new/') {
    return last ? navigateTo(`/sites/${last}/materials/new`) : goSites()
  }

  const mat = to.path.match(/^\/materials\/([^/]+)\/?$/)
  if (mat && !['usage', 'new'].includes(mat[1])) {
    return last ? navigateTo(`/sites/${last}/materials/${mat[1]}`) : goSites()
  }
})
