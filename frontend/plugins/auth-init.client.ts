/** Sync Pinia auth state from localStorage after Pinia is installed. */
export default defineNuxtPlugin(() => {
  useAuthStore().hydrateFromStorage()
})
