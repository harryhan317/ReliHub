import api from './api';
import type { ApiResponse, AISession, AIMessage, PaginatedResponse } from '../types';

export const aiService = {
  async getSessions(page = 1, pageSize = 20) {
    const res = await api.get<ApiResponse<PaginatedResponse<AISession>>>('/ai/sessions', {
      params: { page, page_size: pageSize },
    });
    return res.data;
  },

  async getSession(sessionId: string) {
    const res = await api.get<ApiResponse<AISession>>(`/ai/sessions/${sessionId}`);
    return res.data;
  },

  async createSession(title: string) {
    const res = await api.post<ApiResponse<AISession>>('/ai/sessions', { title });
    return res.data;
  },

  async deleteSession(sessionId: string) {
    const res = await api.delete<ApiResponse>(`/ai/sessions/${sessionId}`);
    return res.data;
  },

  async getMessages(sessionId: string, page = 1, pageSize = 50) {
    const res = await api.get<ApiResponse<PaginatedResponse<AIMessage>>>(`/ai/sessions/${sessionId}/messages`, {
      params: { page, page_size: pageSize },
    });
    return res.data;
  },

  async sendMessage(sessionId: string, content: string, stream = false) {
    const res = await api.post<ApiResponse<AIMessage>>(`/ai/sessions/${sessionId}/messages`, { content, stream });
    return res.data;
  },

  async likeMessage(sessionId: string, messageId: string) {
    const res = await api.post<ApiResponse>(`/ai/sessions/${sessionId}/feedback`, { message_id: messageId, feedback_type: 'like' });
    return res.data;
  },

  async dislikeMessage(sessionId: string, messageId: string) {
    const res = await api.post<ApiResponse>(`/ai/sessions/${sessionId}/feedback`, { message_id: messageId, feedback_type: 'dislike' });
    return res.data;
  },

  getStreamUrl(sessionId: string) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    return `${baseUrl}/ai/sessions/${sessionId}/messages`;
  },
};
