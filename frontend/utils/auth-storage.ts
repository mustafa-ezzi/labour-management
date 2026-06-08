/** Token persistence — safe to read before Pinia is ready (middleware, early plugins). */

export const AUTH_STORAGE_KEY = 'lms_auth'

type Stored = {
  access: string
  refresh: string
}

export function readAuthFromStorage(): Stored | null {
  if (!import.meta.client) return null
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) return null
    const data = JSON.parse(raw) as Stored
    if (!data.access || !data.refresh) return null
    return data
  } catch {
    localStorage.removeItem(AUTH_STORAGE_KEY)
    return null
  }
}

export function writeAuthToStorage(access: string, refresh: string) {
  if (!import.meta.client) return
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ access, refresh }))
}

export function clearAuthStorage() {
  if (!import.meta.client) return
  localStorage.removeItem(AUTH_STORAGE_KEY)
}

export function hasStoredAuth(): boolean {
  return readAuthFromStorage() !== null
}
