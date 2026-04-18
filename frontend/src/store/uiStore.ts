import { create } from 'zustand';

interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
}

interface UIStore {
  activeTab: string;
  toasts: Toast[];
  modals: Record<string, boolean>;
  searchType: 'RESOURCE' | 'COMMUNITY' | 'AI';

  setActiveTab: (tab: string) => void;
  showToast: (message: string, type?: 'success' | 'error' | 'info') => void;
  removeToast: (id: string) => void;
  showModal: (modalId: string) => void;
  hideModal: (modalId: string) => void;
  setSearchType: (type: 'RESOURCE' | 'COMMUNITY' | 'AI') => void;
}

let toastCounter = 0;

export const useUIStore = create<UIStore>((set) => ({
  activeTab: 'ask',
  toasts: [],
  modals: {},
  searchType: 'RESOURCE',

  setActiveTab: (tab) => set({ activeTab: tab }),

  showToast: (message, type = 'info') => {
    const id = `toast-${++toastCounter}`;
    set((state) => ({
      toasts: [...state.toasts, { id, message, type }],
    }));
    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
      }));
    }, 2500);
  },

  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),

  showModal: (modalId) =>
    set((state) => ({
      modals: { ...state.modals, [modalId]: true },
    })),

  hideModal: (modalId) =>
    set((state) => ({
      modals: { ...state.modals, [modalId]: false },
    })),

  setSearchType: (type) => set({ searchType: type }),
}));
