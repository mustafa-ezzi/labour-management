import { defineStore } from 'pinia'
import {
  clearAuthStorage,
  readAuthFromStorage,
  writeAuthToStorage,
} from '~/utils/auth-storage'
import { tokenIsAppAdmin } from '~/utils/jwt'

const ADMIN_FLAG_KEY = 'lms_is_app_admin'

function readAdminFlag(): boolean {
  if (!import.meta.client) return false
  return localStorage.getItem(ADMIN_FLAG_KEY) === '1'
}

function writeAdminFlag(value: boolean) {
  if (!import.meta.client) return
  if (value) localStorage.setItem(ADMIN_FLAG_KEY, '1')
  else localStorage.removeItem(ADMIN_FLAG_KEY)
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null as string | null,
    refreshToken: null as string | null,
    /** Explicit Admin flag — survives JWT decode quirks / old tokens without claim */
    appAdminVerified: false,
  }),
  getters: {
    isLoggedIn: (s) => Boolean(s.accessToken),
    isAppAdmin: (s) => s.appAdminVerified || tokenIsAppAdmin(s.accessToken),
  },
  actions: {
    hydrateFromStorage() {
      const data = readAuthFromStorage()
      if (!data) {
        this.accessToken = null
        this.refreshToken = null
        this.appAdminVerified = false
        return
      }
      this.accessToken = data.access
      this.refreshToken = data.refresh
      this.appAdminVerified = readAdminFlag() || tokenIsAppAdmin(data.access)
      if (this.appAdminVerified) writeAdminFlag(true)
    },
    setTokens(access: string, refresh: string) {
      this.accessToken = access
      this.refreshToken = refresh
      writeAuthToStorage(access, refresh)
      if (tokenIsAppAdmin(access)) {
        this.appAdminVerified = true
        writeAdminFlag(true)
      }
    },
    setAppAdminVerified(value: boolean) {
      this.appAdminVerified = value
      writeAdminFlag(value)
    },
    clear() {
      this.accessToken = null
      this.refreshToken = null
      this.appAdminVerified = false
      clearAuthStorage()
      writeAdminFlag(false)
      if (import.meta.client) {
        localStorage.removeItem('lm:lastSiteId')
        // Guided-tour state is a global useState singleton that survives client-side
        // navigation. Without this, a tour interrupted by sign-out (or a forced
        // logout from a 401/disabled-account redirect) stays "active" in memory and
        // can re-render as a blocking overlay next time someone logs in on this tab —
        // looking like login "doesn't work" until a hard refresh resets the state.
        try {
          useOnboardingTour().abort()
        } catch {
          document.body.classList.remove('tour-open')
        }
      }
    },
  },
})
