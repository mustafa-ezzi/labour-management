export type MaterialsTab = {
  to: string
  label: string
  section: 'list' | 'usage'
}

export function useMaterialsNav() {
  const route = useRoute()

  const tabs = computed((): MaterialsTab[] => {
    const siteId = route.params.siteId as string | undefined
    if (!siteId) {
      return []
    }
    const base = `/sites/${siteId}/materials`
    return [
      { to: base, label: 'Materials', section: 'list' },
      { to: `${base}/usage`, label: 'Log usage', section: 'usage' },
    ]
  })

  return { tabs }
}
