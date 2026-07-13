<template>
  <div class="mx-auto max-w-md px-4 py-16 text-center">
    <img src="/logo.png" alt="LabourPro" class="mx-auto h-16 w-16 rounded-2xl object-contain" />
    <h1 class="mt-6 text-2xl font-black text-gray-900">Access paused</h1>
    <p class="mt-2 text-sm text-gray-600">
      Your account is disabled or your plan has ended. Contact LabourPro support to continue.
    </p>
    <div class="mt-8 flex flex-col gap-3">
      <NuxtLink to="/login" class="ui-btn-primary w-full py-3">Back to sign in</NuxtLink>
      <button type="button" class="ui-btn-secondary w-full py-3" @click="signOut">
        Sign out
      </button>
    </div>
    <p class="mt-6 text-xs text-gray-400">
      Full subscription end-date UI ships in Phase 3; support tickets in Phase 4.
    </p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const auth = useAuthStore()
const router = useRouter()

async function signOut() {
  auth.clear()
  await router.push('/login')
}
</script>
