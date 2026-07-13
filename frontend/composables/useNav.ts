export type NavItem = {
  to: string
  label: string
  shortLabel: string
  icon: string
  /** What kind of path-match marks this tab as active */
  match: 'exact' | 'prefix'
  /** Optional extra prefix (e.g. /sites/:id) used only for the All sites entry */
  prefix?: string
}

export function useAppNav() {
  const route = useRoute()

  const items = computed((): NavItem[] => {
    const siteId = typeof route.params.siteId === 'string' ? route.params.siteId : ''
    if (siteId) {
      const base = `/sites/${siteId}`
      return [
        { to: base, label: 'Overview', shortLabel: 'Site', icon: 'site', match: 'exact' },
        { to: `${base}/crew`, label: 'Crew', shortLabel: 'Crew', icon: 'crew', match: 'prefix', prefix: `${base}/crew` },
        { to: `${base}/materials`, label: 'Materials', shortLabel: 'Mat.', icon: 'materials', match: 'prefix', prefix: `${base}/materials` },
        { to: '/sites', label: 'All sites', shortLabel: 'Sites', icon: 'home', match: 'exact' },
      ]
    }

    return [
      { to: '/dashboard', label: 'Dashboard', shortLabel: 'Home', icon: 'home', match: 'exact' },
      { to: '/sites', label: 'Sites', shortLabel: 'Sites', icon: 'site', match: 'prefix', prefix: '/sites' },
      {
        to: '/subscription',
        label: 'Subscription',
        shortLabel: 'Plan',
        icon: 'pay',
        match: 'exact',
      },
    ]
  })

  function isActive(item: NavItem): boolean {
    const path = (route.path.replace(/\/$/, '') || route.path)
    if (item.match === 'exact') {
      return path === item.to
    }
    const pref = item.prefix ?? item.to
    return path === pref || path.startsWith(`${pref}/`)
  }

  /** Bottom grid: 3 columns when browsing globally, 4 when inside a site */
  const bottomNavClass = computed(() =>
    route.params.siteId ? 'grid-cols-4' : 'grid-cols-3',
  )

  return { items, bottomNavClass, isActive }
}
