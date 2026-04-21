import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from './authStore';
import { useGuestStore } from './guestStore';

const GUEST_LIMIT_REASONS: Record<string, string> = {
  ai_limit: '今日AI对话次数已达上限',
  resource_limit: '游客仅可浏览10条资源',
  community_limit: '游客仅可浏览10条话题',
  download: '下载资源需要注册登录',
  collect: '收藏功能需要注册登录',
  like: '点赞功能需要注册登录',
  comment: '评论功能需要注册登录',
  upload: '上传资源需要注册登录',
  new_topic: '发起话题需要注册登录',
  open_my: '查看个人中心需要注册登录',
  reply: '回复话题需要注册登录',
  report: '举报功能需要注册登录',
};

export const useGuestGuard = () => {
  const { isGuest } = useAuthStore();
  const navigate = useNavigate();
  const guestStore = useGuestStore();
  const [guideModal, setGuideModal] = useState<{
    open: boolean;
    source: string;
    reason: string;
  }>({ open: false, source: '', reason: '' });

  const checkAction = useCallback((action: string): boolean => {
    if (!isGuest) return true;

    const reason = GUEST_LIMIT_REASONS[action] || '该功能需要注册登录';

    if (action === 'ai_limit') {
      if (!guestStore.canCreateAISession()) {
        if (guestStore.shouldShowGuide(action)) {
          setGuideModal({ open: true, source: action, reason });
        }
        return false;
      }
      return true;
    }

    if (action === 'resource_limit') {
      if (!guestStore.canViewResource()) {
        if (guestStore.shouldShowGuide(action)) {
          setGuideModal({ open: true, source: action, reason });
        }
        return false;
      }
      return true;
    }

    if (action === 'community_limit') {
      if (!guestStore.canViewCommunity()) {
        if (guestStore.shouldShowGuide(action)) {
          setGuideModal({ open: true, source: action, reason });
        }
        return false;
      }
      return true;
    }

    const restrictedActions = ['download', 'collect', 'like', 'comment', 'upload', 'new_topic', 'open_my', 'reply', 'report'];
    if (restrictedActions.includes(action)) {
      if (guestStore.shouldShowGuide(action)) {
        setGuideModal({ open: true, source: action, reason });
      }
      return false;
    }

    return true;
  }, [isGuest, guestStore]);

  const closeGuideModal = useCallback(() => {
    setGuideModal((prev) => ({ ...prev, open: false }));
  }, []);

  const navigateToLogin = useCallback((source: string) => {
    const params = new URLSearchParams({
      source_scene: source,
      trigger_action: source,
      trigger_time: new Date().toISOString(),
    });
    navigate(`/login?${params.toString()}`);
  }, [navigate]);

  return {
    checkAction,
    guideModal,
    closeGuideModal,
    navigateToLogin,
    isGuest,
  };
};
