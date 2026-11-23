import axios from 'axios'

// Empty in local dev, so requests stay on the Vite proxy. Vercel sets VITE_API_URL at build time.
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('finscope_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = error.config?.url || ''
    const isLogin = url.includes('/auth/login')
    if (error.response?.status === 401 && !isLogin) {
      localStorage.removeItem('finscope_token')
      if (!window.location.pathname.startsWith('/login')) {
        window.location.assign('/login')
      }
    }
    return Promise.reject(error)
  },
)

export function errorMessage(error) {
  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).filter(Boolean).join(' ')
  }
  if (!error.response || error.response.status >= 500) {
    return 'The API is not running. Start the backend and try again.'
  }
  return 'Something went wrong. Try again.'
}
