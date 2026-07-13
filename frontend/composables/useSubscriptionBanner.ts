export type SubscriptionInfo = {
  status: string
  ends_at: string
  days_remaining: number
  ending_soon: boolean
  is_expired: boolean
  message: string | null
  plan: { name: string; key: string } | null
  company_name?: string
}

/** Shared subscription status for banners (alerts only — never gates the app). */
export function useSubscriptionBanner() {
  const api = createApiClient()
  const auth = useAuthStore()
  const info = useState<SubscriptionInfo | null>('subscription-banner', () => null)
  const loaded = useState('subscription-banner-loaded', () => false)

  async function refresh() {
    if (!auth.accessToken || auth.isAppAdmin) {
      info.value = null
      loaded.value = true
      return
    }
    try {
      const { data } = await api.get<SubscriptionInfo>('/subscription/me/')
      info.value = data
    } catch {
      info.value = null
    } finally {
      loaded.value = true
    }
  }

  const showBanner = computed(() => {
    if (!info.value) return false
    return Boolean(info.value.is_expired || info.value.ending_soon)
  })

  return { info, loaded, showBanner, refresh }
}
