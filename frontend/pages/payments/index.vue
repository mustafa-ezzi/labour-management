<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

const route = useRoute()
const cookie = useCookie<string | null>(LAST_SITE_COOKIE_NAME, lastSiteCookieOpts)
const id = readResolvedLastSiteId(cookie.value)

await navigateTo(
  id
    ? {
        path: `/sites/${id}/crew/wages`,
        query: route.query,
      }
    : '/sites',
  { replace: true },
)
</script>
