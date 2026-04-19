import api from './api';
import type {
  DashboardStats,
  AdminUserListResponse,
  ResourceListResponse,
  TopicListResponse,
  FeedbackListResponse,
  AuditLogListResponse,
  SystemConfigListResponse,
  SystemConfig,
  LLMProvider,
  AssetPackage,
} from '@/types';

interface AdminLoginData {
  access_token: string;
  refresh_token: string;
  admin_info: { id: string; username: string; role: string };
}

export const adminService = {
  async login(username: string, password: string): Promise<AdminLoginData> {
    const res = await api.post<{ code: string; msg: string; data: AdminLoginData }>('/admin/auth/login', { username, password });
    if (res.data.code !== '000000') throw new Error(res.data.msg || '登录失败');
    const d = res.data.data;
    localStorage.setItem('admin_access_token', d.access_token);
    localStorage.setItem('admin_user', JSON.stringify(d.admin_info));
    return d;
  },

  async logout() {
    try { await api.post('/admin/auth/logout'); } finally {
      localStorage.removeItem('admin_access_token');
      localStorage.removeItem('admin_user');
    }
  },

  async getDashboardStats(): Promise<DashboardStats> {
    const res = await api.get<DashboardStats>('/admin/dashboard/stats');
    return res.data;
  },

  async getUsers(params?: { status?: string; search?: string; page?: number; page_size?: number }): Promise<AdminUserListResponse> {
    const res = await api.get<AdminUserListResponse>('/admin/users', { params });
    return res.data;
  },

  async getUserDetail(userId: string) {
    const res = await api.get(`/admin/users/${userId}`);
    return res.data;
  },

  async banUser(userId: string, reason: string, durationDays?: number) {
    const res = await api.post(`/admin/users/${userId}/ban`, { reason, duration_days: durationDays });
    return res.data;
  },

  async unbanUser(userId: string) {
    const res = await api.post(`/admin/users/${userId}/unban`);
    return res.data;
  },

  async lockUser(userId: string, reason: string) {
    const res = await api.post(`/admin/users/${userId}/lock`, { reason });
    return res.data;
  },

  async unlockUser(userId: string) {
    const res = await api.post(`/admin/users/${userId}/unlock`);
    return res.data;
  },

  async getResources(params?: { status?: string; page?: number; page_size?: number }): Promise<ResourceListResponse> {
    const res = await api.get<ResourceListResponse>('/admin/resources', { params });
    return res.data;
  },

  async getPendingResources(params?: { page?: number; page_size?: number }): Promise<ResourceListResponse> {
    const res = await api.get<ResourceListResponse>('/admin/resources/pending', { params });
    return res.data;
  },

  async approveResource(resourceId: string, reason?: string) {
    const res = await api.post(`/admin/resources/${resourceId}/approve`, { reason });
    return res.data;
  },

  async rejectResource(resourceId: string, reason: string) {
    const res = await api.post(`/admin/resources/${resourceId}/reject`, { reason });
    return res.data;
  },

  async blockResource(resourceId: string, reason: string) {
    const res = await api.post(`/admin/resources/${resourceId}/block`, { reason });
    return res.data;
  },

  async getTopics(params?: { status?: string; page?: number; page_size?: number }): Promise<TopicListResponse> {
    const res = await api.get<TopicListResponse>('/admin/topics', { params });
    return res.data;
  },

  async blockTopic(topicId: string, reason: string) {
    const res = await api.post(`/admin/topics/${topicId}/block`, { reason });
    return res.data;
  },

  async getFeedbacks(params?: { status?: string; page?: number; page_size?: number }): Promise<FeedbackListResponse> {
    const res = await api.get<FeedbackListResponse>('/admin/feedbacks', { params });
    return res.data;
  },

  async replyFeedback(feedbackId: string, reply: string) {
    const res = await api.post(`/admin/feedbacks/${feedbackId}/reply`, { reply });
    return res.data;
  },

  async getAuditLogs(params?: { admin_id?: string; action?: string; page?: number; page_size?: number }): Promise<AuditLogListResponse> {
    const res = await api.get<AuditLogListResponse>('/admin/audit-logs', { params });
    return res.data;
  },

  async getSystemConfigs(): Promise<SystemConfigListResponse> {
    const res = await api.get<SystemConfigListResponse>('/admin/system-configs');
    return res.data;
  },

  async updateSystemConfig(configKey: string, configValue: string, description?: string): Promise<SystemConfig> {
    const res = await api.patch<SystemConfig>('/admin/system-configs', { config_key: configKey, config_value: configValue, description });
    return res.data;
  },

  async getLLMProviders(): Promise<LLMProvider[]> {
    const res = await api.get<{ items: LLMProvider[] }>('/admin/llm-providers');
    return res.data?.items || [];
  },

  async createLLMProvider(data: Partial<LLMProvider>): Promise<LLMProvider> {
    const res = await api.post<LLMProvider>('/admin/llm-providers', data);
    return res.data;
  },

  async updateLLMProvider(providerId: string, data: Partial<LLMProvider>): Promise<LLMProvider> {
    const res = await api.put<LLMProvider>(`/admin/llm-providers/${providerId}`, data);
    return res.data;
  },

  async deleteLLMProvider(providerId: string) {
    await api.delete(`/admin/llm-providers/${providerId}`);
  },

  async testLLMProvider(providerId: string) {
    const res = await api.post(`/admin/llm-providers/${providerId}/test`);
    return res.data;
  },

  async getAssetPackages(): Promise<AssetPackage[]> {
    const res = await api.get<{ items: AssetPackage[] }>('/admin/asset-packages');
    return res.data?.items || [];
  },

  async updateAssetPackage(packageId: string, data: Partial<AssetPackage>): Promise<AssetPackage> {
    const res = await api.patch<AssetPackage>(`/admin/asset-packages/${packageId}`, data);
    return res.data;
  },
};
