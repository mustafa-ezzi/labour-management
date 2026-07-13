<script setup lang="ts">
import { hasStoredAuth, readAuthFromStorage } from '~/utils/auth-storage'
import { tokenIsAppAdmin } from '~/utils/jwt'

if (import.meta.client) {
  if (!hasStoredAuth()) {
    await navigateTo('/login')
  } else {
    const stored = readAuthFromStorage()
    await navigateTo(tokenIsAppAdmin(stored?.access) ? '/admin' : '/dashboard')
  }
}
</script>
