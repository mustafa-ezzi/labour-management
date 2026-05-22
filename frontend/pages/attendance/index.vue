<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

const cookie = useCookie<string | null>(LAST_SITE_COOKIE_NAME, lastSiteCookieOpts)
const id = readResolvedLastSiteId(cookie.value)

await navigateTo(id ? `/sites/${id}/crew/attendance` : '/sites', { replace: true })
</script>
