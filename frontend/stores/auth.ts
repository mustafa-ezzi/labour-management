import { defineStore } from 'pinia'

const STORAGE_KEY = 'lms_auth'

type Stored = {
  access: string
  refresh: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null as string | null,
    refreshToken: null as string | null,
  }),
  getters: {
    isLoggedIn: (s) => Boolean(s.accessToken),
  },
  actions: {
    hydrateFromStorage() {
      if (!import.meta.client) return
      try {
        const raw = localStorage.getItem(STORAGE_KEY)
        if (!raw) return
        const data = JSON.parse(raw) as Stored
        this.accessToken = data.access
        this.refreshToken = data.refresh
      } catch {
        this.clear()
      }
    },
    setTokens(access: string, refresh: string) {
      this.accessToken = access
      this.refreshToken = refresh
      if (import.meta.client) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ access, refresh }))
      }
    },
    clear() {
      this.accessToken = null
      this.refreshToken = null
      if (import.meta.client) {
        localStorage.removeItem(STORAGE_KEY)
      }
    },
  },
})
