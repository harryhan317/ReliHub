import { create } from 'zustand';
import type { User } from '../types';
import { authService } from '../services/authService';

interface AuthStore {
  isGuest: boolean;
  isLoggedIn: boolean;
  isNewUser: boolean;
  user: User | null;
  accessToken: string | null;

  init: () => void;
  login: (phone: string, password: string) => Promise<void>;
  loginByCode: (phone: string, code: string) => Promise<void>;
  register: (phone: string, code: string, password?: string) => Promise<void>;
  wechatLogin: (code: string) => Promise<void>;
  logout: () => void;
  updateUser: (data: Partial<User>) => void;
  setGuest: () => void;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  isGuest: true,
  isLoggedIn: false,
  isNewUser: false,
  user: null,
  accessToken: null,

  init: () => {
    const token = localStorage.getItem('access_token');
    const userStr = localStorage.getItem('user');
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr) as User;
        set({
          isGuest: false,
          isLoggedIn: true,
          accessToken: token,
          user,
        });
      } catch {
        set({ isGuest: true, isLoggedIn: false });
      }
    } else {
      set({ isGuest: true, isLoggedIn: false });
    }
  },

  login: async (phone, password) => {
    const res = await authService.login(phone, password);
    set({
      isGuest: false,
      isLoggedIn: true,
      isNewUser: false,
      accessToken: res.access_token,
      user: res.user,
    });
  },

  loginByCode: async (phone, code) => {
    const res = await authService.register(phone, code);
    set({
      isGuest: false,
      isLoggedIn: true,
      isNewUser: res.is_new_user,
      accessToken: res.access_token,
      user: res.user,
    });
  },

  register: async (phone, code, password) => {
    const res = await authService.register(phone, code, password);
    set({
      isGuest: false,
      isLoggedIn: true,
      isNewUser: res.is_new_user,
      accessToken: res.access_token,
      user: res.user,
    });
  },

  wechatLogin: async (code) => {
    const res = await authService.wechatLogin(code);
    set({
      isGuest: false,
      isLoggedIn: true,
      isNewUser: res.is_new_user,
      accessToken: res.access_token,
      user: res.user,
    });
  },

  logout: () => {
    authService.logout();
    set({
      isGuest: true,
      isLoggedIn: false,
      isNewUser: false,
      user: null,
      accessToken: null,
    });
  },

  updateUser: (data) => {
    const currentUser = get().user;
    if (currentUser) {
      const updatedUser = { ...currentUser, ...data };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      set({ user: updatedUser });
    }
  },

  setGuest: () => {
    set({
      isGuest: true,
      isLoggedIn: false,
      isNewUser: false,
      user: null,
      accessToken: null,
    });
  },
}));
