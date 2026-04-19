import { create } from 'zustand';

interface AdminUser {
  id: string;
  username: string;
  role: 'SUPER_ADMIN' | 'OPERATOR' | 'AUDITOR';
}

interface AdminStore {
  isLoggedIn: boolean;
  adminUser: AdminUser | null;
  init: () => void;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAdminStore = create<AdminStore>((set) => ({
  isLoggedIn: false,
  adminUser: null,

  init: () => {
    const token = localStorage.getItem('admin_access_token');
    const userStr = localStorage.getItem('admin_user');
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        set({ isLoggedIn: true, adminUser: user });
      } catch {
        localStorage.removeItem('admin_access_token');
        localStorage.removeItem('admin_user');
      }
    }
  },

  login: async (username: string, password: string) => {
    const { adminService } = await import('@/services/adminService');
    const res = await adminService.login(username, password);
    set({ isLoggedIn: true, adminUser: res.admin_info as AdminUser });
  },

  logout: () => {
    import('@/services/adminService').then(({ adminService }) => adminService.logout());
    set({ isLoggedIn: false, adminUser: null });
  },
}));
