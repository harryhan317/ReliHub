import api from './api';
import type { User } from '../types';

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_info: {
    id: string;
    nickname: string;
    avatar_url: string | null;
    rank: string;
    reputation_points: number;
    gold_beans: number;
    bonus_beans: number;
    is_reward_triggered: boolean;
    is_new_user: boolean;
  };
}

function mapUserInfoToUser(info: TokenResponse['user_info']): User {
  return {
    id: info.id,
    phone: '',
    nickname: info.nickname,
    avatar_url: info.avatar_url || '',
    gender: '',
    company: '',
    position: '',
    email: '',
    level: info.rank,
    credit_score: info.reputation_points,
    cocoa_beans: info.gold_beans + info.bonus_beans,
    reputation_points: info.reputation_points,
    is_guest: false,
    checked_in_today: false,
    early_bird_available: false,
    early_bird_count: 0,
    created_at: new Date().toISOString(),
  };
}

function saveAuth(resp: TokenResponse): User {
  const user = mapUserInfoToUser(resp.user_info);
  localStorage.setItem('access_token', resp.access_token);
  localStorage.setItem('refresh_token', resp.refresh_token);
  localStorage.setItem('user', JSON.stringify(user));
  return user;
}

export const authService = {
  async sendSmsCode(phone: string) {
    const res = await api.post('/auth/send-code', { phone });
    return res.data;
  },

  async login(phone: string, password: string) {
    const res = await api.post<TokenResponse>('/auth/login', { phone, password });
    const user = saveAuth(res.data);
    return { access_token: res.data.access_token, user, is_new_user: res.data.user_info.is_new_user };
  },

  async register(phone: string, code: string, password?: string) {
    const res = await api.post<TokenResponse>('/auth/register', {
      phone,
      code,
      password,
      agreed_to_terms: true,
    });
    const user = saveAuth(res.data);
    return { access_token: res.data.access_token, user, is_new_user: res.data.user_info.is_new_user };
  },

  async wechatLogin(code: string) {
    const res = await api.post<TokenResponse>('/auth/wechat-login', { code });
    const user = saveAuth(res.data);
    return { access_token: res.data.access_token, user, is_new_user: res.data.user_info.is_new_user };
  },

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    const res = await api.post<{ access_token: string; refresh_token: string; token_type: string }>('/auth/refresh', { refresh_token: refreshToken });
    if (res.data.access_token) {
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('refresh_token', res.data.refresh_token);
    }
    return res.data;
  },

  async logout() {
    try {
      await api.post('/auth/logout');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  async resetPassword(phone: string, code: string, password: string) {
    const res = await api.post('/auth/reset-password', { phone, code, password });
    return res.data;
  },

  async updateProfile(data: Partial<User>) {
    const res = await api.put<User>('/users/me', data);
    if (res.data) {
      localStorage.setItem('user', JSON.stringify(res.data));
    }
    return res.data;
  },

  async getProfile() {
    const res = await api.get<User>('/users/me');
    if (res.data) {
      localStorage.setItem('user', JSON.stringify(res.data));
    }
    return res.data;
  },
};
