<template>
  <div class="mx-auto max-w-md px-4 py-16 text-center">
    <img src="/logo.png" alt="LabourPro" class="mx-auto h-16 w-16 rounded-2xl object-contain" />
    <h1 class="mt-6 text-2xl font-black text-gray-900">Account disabled</h1>
    <p class="mt-2 text-sm text-gray-600">
      Your login has been disabled by LabourPro Admin. Contact support if you think this is a
      mistake.
    </p>
    <p class="mt-3 text-xs text-gray-500">
      An ended subscription alone does not lock you out — only a manual Admin disable does.
    </p>
    <div class="mt-8 flex flex-col gap-3">
      <NuxtLink to="/login" class="ui-btn-primary w-full py-3">Back to sign in</NuxtLink>
      <button type="button" class="ui-btn-secondary w-full py-3" @click="signOut">
        Sign out
      </button>
    </div>
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
