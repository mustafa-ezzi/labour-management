<script setup lang="ts">
import { hasStoredAuth } from '~/utils/auth-storage'

if (import.meta.client) {
  await navigateTo(hasStoredAuth() ? '/dashboard' : '/login')
}
</script>
