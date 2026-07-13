import axios, { type AxiosInstance } from 'axios'

export function createApiClient(): AxiosInstance {
  const config = useRuntimeConfig()
  const auth = useAuthStore()

  const client = axios.create({
    baseURL: config.public.apiBase as string,
    headers: { 'Content-Type': 'application/json' },
  })

  client.interceptors.request.use((req) => {
    if (auth.accessToken) {
      req.headers.Authorization = `Bearer ${auth.accessToken}`
    }
    return req
  })

  client.interceptors.response.use(
    (res) => res,
    async (error) => {
      const original = error.config
      const status = error.response?.status
      const detail = String(error.response?.data?.detail || '')

      if (
        import.meta.client &&
        status === 403 &&
        /disabled|subscription|plan ended|expired/i.test(detail)
      ) {
        const path = window.location.pathname
        if (!path.startsWith('/subscription-ended') && !path.startsWith('/login')) {
          await navigateTo('/subscription-ended')
        }
      }

      if (status === 401 && auth.refreshToken && !original._retry) {
        original._retry = true
        try {
          const { data } = await axios.post(`${config.public.apiBase}/auth/refresh/`, {
            refresh: auth.refreshToken,
          })
          const newRefresh = (data as { access: string; refresh?: string }).refresh
          auth.setTokens(data.access, newRefresh ?? auth.refreshToken)
          original.headers.Authorization = `Bearer ${data.access}`
          return client(original)
        } catch {
          auth.clear()
        }
      }
      return Promise.reject(error)
    },
  )

  return client
}
