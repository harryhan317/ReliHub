import { create } from 'zustand';

const GUEST_AI_DAILY_SESSIONS = 3;
const GUEST_BROWSE_LIMIT = 10;
const GUIDE_THROTTLE_MS = 60000;

interface GuestLimitState {
  aiSessionsUsed: number;
  aiSessionDate: string;
  resourceViewed: number;
  communityViewed: number;
  lastGuideTime: Record<string, number>;

  canCreateAISession: () => boolean;
  incrementAISession: () => void;
  canViewResource: () => boolean;
  incrementResourceView: () => void;
  canViewCommunity: () => boolean;
  incrementCommunityView: () => void;
  shouldShowGuide: (source: string) => boolean;
  markGuideShown: (source: string) => void;
  resetDailyIfNeeded: () => void;
}

const getTodayStr = () => new Date().toISOString().slice(0, 10);

export const useGuestStore = create<GuestLimitState>((set, get) => ({
  aiSessionsUsed: parseInt(localStorage.getItem('guest_ai_sessions_used') || '0', 10),
  aiSessionDate: localStorage.getItem('guest_ai_date') || '',
  resourceViewed: parseInt(localStorage.getItem('guest_resource_viewed') || '0', 10),
  communityViewed: parseInt(localStorage.getItem('guest_community_viewed') || '0', 10),
  lastGuideTime: JSON.parse(localStorage.getItem('guest_guide_times') || '{}'),

  canCreateAISession: () => {
    get().resetDailyIfNeeded();
    return get().aiSessionsUsed < GUEST_AI_DAILY_SESSIONS;
  },

  incrementAISession: () => {
    const today = getTodayStr();
    set((state) => {
      const newCount = state.aiSessionDate === today ? state.aiSessionsUsed + 1 : 1;
      localStorage.setItem('guest_ai_sessions_used', newCount.toString());
      localStorage.setItem('guest_ai_date', today);
      return { aiSessionsUsed: newCount, aiSessionDate: today };
    });
  },

  canViewResource: () => {
    get().resetDailyIfNeeded();
    return get().resourceViewed < GUEST_BROWSE_LIMIT;
  },

  incrementResourceView: () => {
    set((state) => {
      const newCount = state.resourceViewed + 1;
      localStorage.setItem('guest_resource_viewed', newCount.toString());
      return { resourceViewed: newCount };
    });
  },

  canViewCommunity: () => {
    get().resetDailyIfNeeded();
    return get().communityViewed < GUEST_BROWSE_LIMIT;
  },

  incrementCommunityView: () => {
    set((state) => {
      const newCount = state.communityViewed + 1;
      localStorage.setItem('guest_community_viewed', newCount.toString());
      return { communityViewed: newCount };
    });
  },

  shouldShowGuide: (source: string) => {
    const lastTime = get().lastGuideTime[source] || 0;
    return Date.now() - lastTime > GUIDE_THROTTLE_MS;
  },

  markGuideShown: (source: string) => {
    set((state) => {
      const newTimes = { ...state.lastGuideTime, [source]: Date.now() };
      localStorage.setItem('guest_guide_times', JSON.stringify(newTimes));
      return { lastGuideTime: newTimes };
    });
  },

  resetDailyIfNeeded: () => {
    const today = getTodayStr();
    const state = get();
    if (state.aiSessionDate !== today) {
      set({ aiSessionsUsed: 0, aiSessionDate: today });
      localStorage.setItem('guest_ai_sessions_used', '0');
      localStorage.setItem('guest_ai_date', today);
    }
  },
}));
