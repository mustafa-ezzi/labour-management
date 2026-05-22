<script setup lang="ts">
if (import.meta.server) {
  await navigateTo('/login')
} else {
  const auth = useAuthStore()
  auth.hydrateFromStorage()
  await navigateTo(auth.isLoggedIn ? '/dashboard' : '/login')
}
</script>
