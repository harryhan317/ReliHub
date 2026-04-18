import api from './api';
import type { ApiResponse, Topic, Reply, PaginatedResponse, CommunityCategory } from '../types';

export const communityService = {
  async getCategories() {
    const res = await api.get<ApiResponse<CommunityCategory[]>>('/community/categories');
    return res.data;
  },

  async getTopics(params: { category?: string; sort?: string; page?: number; page_size?: number }) {
    const res = await api.get<ApiResponse<PaginatedResponse<Topic>>>('/community/topics', { params });
    return res.data;
  },

  async getTopic(id: string) {
    const res = await api.get<ApiResponse<Topic & { replies: Reply[] }>>(`/community/topics/${id}`);
    return res.data;
  },

  async createTopic(data: { title: string; content: string; category: string; bounty?: number }) {
    const res = await api.post<ApiResponse<Topic>>('/community/topics', data);
    return res.data;
  },

  async createReply(topicId: string, content: string) {
    const res = await api.post<ApiResponse<Reply>>(`/community/topics/${topicId}/replies`, { content });
    return res.data;
  },

  async likeTopic(id: string) {
    const res = await api.post<ApiResponse>(`/community/topics/${id}/like`);
    return res.data;
  },

  async adoptReply(topicId: string, replyId: string) {
    const res = await api.post<ApiResponse>(`/community/topics/${topicId}/adopt/${replyId}`);
    return res.data;
  },

  async followTopic(id: string) {
    const res = await api.post<ApiResponse>(`/community/topics/${id}/follow`);
    return res.data;
  },

  async reportTopic(id: string, reason: string) {
    const res = await api.post<ApiResponse>(`/community/topics/${id}/report`, { reason });
    return res.data;
  },

  async getMyTopics(params: { type?: string; page?: number; page_size?: number }) {
    const res = await api.get<ApiResponse<PaginatedResponse<Topic>>>('/community/my-topics', { params });
    return res.data;
  },
};
