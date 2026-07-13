/** Decode JWT payload (no signature verify — API enforces auth). */
export function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const part = token.split('.')[1]
    if (!part) return null
    const json = atob(part.replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(json) as Record<string, unknown>
  } catch {
    return null
  }
}

export function tokenIsAppAdmin(accessToken: string | null | undefined): boolean {
  if (!accessToken) return false
  const payload = decodeJwtPayload(accessToken)
  return payload?.is_app_admin === true
}
