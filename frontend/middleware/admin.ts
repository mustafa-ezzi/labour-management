import { readAuthFromStorage } from '~/utils/auth-storage'

/**
 * Guard /admin/** — App Admin only.
 * Verifies JWT claim, then falls back to GET /api/admin/me/ (superuser check).
 * Non-admins are signed out and sent to login so they can use the Admin account.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return

  const stored = readAuthFromStorage()
  const pinia = useNuxtApp().$pinia
  const auth = pinia ? useAuthStore(pinia) : useAuthStore()

  if (!stored && !auth.accessToken) {
    return navigateTo(
      {
        path: '/login',
        query: { next: to.fullPath, admin: '1' },
      },
      { replace: true, external: false },
    )
  }

  if (!auth.accessToken && stored) {
    auth.setTokens(stored.access, stored.refresh)
  }

  if (auth.isAppAdmin) return

  // Claim missing (old token) — confirm with API
  try {
    const api = createApiClient()
    await api.get('/admin/me/')
    auth.setAppAdminVerified(true)
    return
  } catch {
    auth.clear()
    return navigateTo(
      {
        path: '/login',
        query: { next: to.fullPath, admin: '1' },
      },
      { replace: true, external: false },
    )
  }
})
