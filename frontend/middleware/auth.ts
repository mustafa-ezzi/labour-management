import { readAuthFromStorage } from '~/utils/auth-storage'

/**
 * Auth guard. Tokens are in localStorage — skip on SSR.
 * Uses storage read first so this works even if Pinia is not active yet.
 */
export default defineNuxtRouteMiddleware(() => {
  if (import.meta.server) {
    return
  }

  const stored = readAuthFromStorage()
  if (!stored) {
    return navigateTo('/login')
  }

  const pinia = useNuxtApp().$pinia
  if (pinia) {
    const auth = useAuthStore(pinia)
    if (!auth.accessToken) {
      auth.setTokens(stored.access, stored.refresh)
    }
  }
})
