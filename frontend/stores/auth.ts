import { defineStore } from 'pinia'
import {
  clearAuthStorage,
  readAuthFromStorage,
  writeAuthToStorage,
} from '~/utils/auth-storage'

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
      const data = readAuthFromStorage()
      if (!data) {
        this.accessToken = null
        this.refreshToken = null
        return
      }
      this.accessToken = data.access
      this.refreshToken = data.refresh
    },
    setTokens(access: string, refresh: string) {
      this.accessToken = access
      this.refreshToken = refresh
      writeAuthToStorage(access, refresh)
    },
    clear() {
      this.accessToken = null
      this.refreshToken = null
      clearAuthStorage()
    },
  },
})
