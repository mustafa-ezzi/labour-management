/** One back control: prefer browser history, else a sensible parent route. */
export function useSmartBack() {
  const router = useRouter()
  const route = useRoute()

  function fallbackPath(): string {
    const siteId = typeof route.params.siteId === 'string' ? route.params.siteId : ''
    const path = route.path.replace(/\/$/, '') || '/'

    if (!siteId) {
      if (path === '/sites/new') return '/sites'
      return '/sites'
    }

    const base = `/sites/${siteId}`
    if (path === base) return '/sites'

    const labourPay = path.match(new RegExp(`^${base}/crew/([^/]+)/payments$`))
    if (labourPay) return `${base}/crew/${labourPay[1]}`

    const labourDetail = path.match(new RegExp(`^${base}/crew/([^/]+)$`))
    if (labourDetail) return `${base}/crew`

    if (path.startsWith(`${base}/crew/`)) return `${base}/crew`

    if (path.match(new RegExp(`^${base}/materials/[^/]+$`))) return `${base}/materials`
    if (path.startsWith(`${base}/materials/`)) return `${base}/materials`

    return base
  }

  function canUseHistory(): boolean {
    if (!import.meta.client) return false
    const state = window.history.state as { position?: number } | null
    return typeof state?.position === 'number' && state.position > 0
  }

  function goBack() {
    if (canUseHistory()) {
      router.back()
      return
    }
    return navigateTo(fallbackPath())
  }

  return { goBack, fallbackPath }
}
