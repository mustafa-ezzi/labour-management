export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()
  if (import.meta.client) {
    auth.hydrateFromStorage()
  }
  if (!auth.isLoggedIn) {
    return navigateTo('/login')
  }
})
