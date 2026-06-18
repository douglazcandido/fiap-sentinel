import axios, { AxiosError } from "axios"
import type { ApiEnvelope } from "./types"
import { MOCK_MODE, getMockData } from "./mock"

export const TOKEN_KEY = "sentinel_token"
export const USER_KEY = "sentinel_user"

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

export const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
})

// Inject Bearer token on every request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Global 401 handler: clear storage and redirect to login.
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      const onLogin = window.location.pathname === "/login"
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
      if (!onLogin) {
        window.location.assign("/login")
      }
    }
    return Promise.reject(error)
  },
)

/** Extracts a human-friendly error message from an axios error. */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: string } | undefined)?.detail
    if (detail) return detail
    if (error.response?.status === 503) return "Serviço temporariamente indisponível."
    if (error.response?.status === 500) return "Erro interno do servidor. Tente novamente."
    if (error.code === "ERR_NETWORK") {
      return "Não foi possível conectar à API. Verifique se o backend está ativo."
    }
    return error.message
  }
  return "Ocorreu um erro inesperado."
}

/** Unwraps the standard { sucesso, mensagem, data } envelope and returns data. */
export async function fetchData<T>(path: string, params?: Record<string, unknown>): Promise<T> {
  if (MOCK_MODE) {
    // Simulate network latency so loading states are visible.
    await new Promise((r) => setTimeout(r, 450))
    return getMockData<T>(path)
  }
  const res = await api.get<ApiEnvelope<T>>(path, { params })
  if (!res.data?.sucesso) {
    throw new Error(res.data?.mensagem || "Falha ao carregar os dados.")
  }
  return res.data.data
}