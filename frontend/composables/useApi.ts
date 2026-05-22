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
      if (error.response?.status === 401 && auth.refreshToken && !original._retry) {
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
