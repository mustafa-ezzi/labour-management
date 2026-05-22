export type NavItem = {
  to: string
  label: string
  shortLabel: string
  icon: string
}

export function useAppNav() {
  const route = useRoute()

  const items = computed((): NavItem[] => {
    const siteId = typeof route.params.siteId === 'string' ? route.params.siteId : ''
    if (siteId) {
      const base = `/sites/${siteId}`
      return [
        { to: base, label: 'Overview', shortLabel: 'Site', icon: 'site' },
        { to: `${base}/crew`, label: 'Crew', shortLabel: 'Crew', icon: 'crew' },
        { to: `${base}/materials`, label: 'Materials', shortLabel: 'Mat.', icon: 'materials' },
        { to: '/sites', label: 'All sites', shortLabel: 'Sites', icon: 'home' },
      ]
    }

    return [
      { to: '/dashboard', label: 'Dashboard', shortLabel: 'Home', icon: 'home' },
      { to: '/sites', label: 'Sites', shortLabel: 'Sites', icon: 'site' },
    ]
  })

  /** Bottom grid: 2 columns when browsing globally, 4 when inside a site */
  const bottomNavClass = computed(() =>
    route.params.siteId ? 'grid-cols-4' : 'grid-cols-2',
  )

  return { items, bottomNavClass }
}
