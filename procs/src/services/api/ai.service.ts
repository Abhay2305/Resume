import { apiGet } from './apiService'
import { API_ENDPOINTS } from './endpoints'
import type {
  AiExecutionListResponse,
  AiExecutionStatsResponse,
  AiTokenResponse,
  AiProviderStatsResponse,
} from '../../types/ai-monitoring'

export async function getAiCosts(params?: Record<string, string | number | boolean | undefined>) {
  return apiGet(API_ENDPOINTS.AI_COSTS, { params })
}

export async function getAiTokens(params?: Record<string, string | number | boolean | undefined>) {
  return apiGet(API_ENDPOINTS.AI_TOKENS, { params })
}

export async function getAiExecutions(params?: Record<string, string | number | boolean | undefined>) {
  return apiGet(API_ENDPOINTS.AI_EXECUTIONS, { params })
}

export async function getAiProviders() {
  return apiGet(API_ENDPOINTS.AI_PROVIDERS)
}

export async function getAiAdminExecutions(params?: Record<string, string | number | boolean | undefined>): Promise<AiExecutionListResponse> {
  return apiGet(API_ENDPOINTS.AI_ADMIN_EXECUTIONS, { params })
}

export async function getAiAdminExecutionStats(params?: Record<string, string | number | boolean | undefined>): Promise<AiExecutionStatsResponse> {
  return apiGet(API_ENDPOINTS.AI_ADMIN_EXECUTION_STATS, { params })
}

export async function getAiAdminTokens(params?: Record<string, string | number | boolean | undefined>): Promise<AiTokenResponse> {
  return apiGet(API_ENDPOINTS.AI_ADMIN_TOKENS, { params })
}

export async function getAiAdminProviders(): Promise<AiProviderStatsResponse> {
  return apiGet(API_ENDPOINTS.AI_ADMIN_PROVIDERS)
}
