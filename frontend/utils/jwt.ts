/** Decode JWT payload (no signature verify — API enforces auth). */
export function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const part = token.split('.')[1]
    if (!part) return null
    const padded = part.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - (part.length % 4)) % 4)
    const json =
      typeof atob === 'function'
        ? atob(padded)
        : Buffer.from(padded, 'base64').toString('utf8')
    return JSON.parse(json) as Record<string, unknown>
  } catch {
    return null
  }
}

export function tokenIsAppAdmin(accessToken: string | null | undefined): boolean {
  if (!accessToken) return false
  const payload = decodeJwtPayload(accessToken)
  const flag = payload?.is_app_admin
  return flag === true || flag === 'true' || flag === 1
}
