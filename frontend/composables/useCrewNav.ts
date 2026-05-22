export type CrewTab = {
  to: string
  label: string
  /** workers | attendance | pay — for highlighting under nested worker routes */
  section: 'workers' | 'attendance' | 'pay'
}

export function useCrewNav() {
  const route = useRoute()

  const tabs = computed((): CrewTab[] => {
    const siteId = route.params.siteId as string | undefined
    if (!siteId) {
      return []
    }
    const base = `/sites/${siteId}/crew`
    return [
      { to: base, label: 'Workers', section: 'workers' },
      { to: `${base}/attendance`, label: 'Attendance', section: 'attendance' },
      { to: `${base}/pay`, label: 'Pay', section: 'pay' },
    ]
  })

  return { tabs }
}
