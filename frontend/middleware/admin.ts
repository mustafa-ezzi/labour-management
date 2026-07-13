export default defineNuxtRouteMiddleware(() => {
  if (import.meta.server) return

  const stored = readAuthFromStorage()
  if (!stored) {
    return navigateTo('/login')
  }

  const pinia = useNuxtApp().$pinia
  const auth = pinia ? useAuthStore(pinia) : useAuthStore()
  if (!auth.accessToken) {
    auth.setTokens(stored.access, stored.refresh)
  }

  if (!auth.isAppAdmin) {
    return navigateTo('/dashboard')
  }
})
