import React, { useEffect } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import PhoneFrame from './layouts/PhoneFrame';
import { useAuthStore } from './store/authStore';

import WelcomePage from './pages/auth/WelcomePage';
import LoginPage from './pages/auth/LoginPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ProfileSetupPage from './pages/auth/ProfileSetupPage';
import AskPage from './pages/ask/AskPage';
import ChatPage from './pages/ask/ChatPage';
import ResourcePage from './pages/resource/ResourcePage';
import ResourceDetailPage from './pages/resource/ResourceDetailPage';
import ResourceUploadPage from './pages/resource/ResourceUploadPage';
import ResourceCategoryPage from './pages/resource/ResourceCategoryPage';
import CommunityPage from './pages/community/CommunityPage';
import TopicDetailPage from './pages/community/TopicDetailPage';
import CommunityCategoryPage from './pages/community/CommunityCategoryPage';
import NewTopicPage from './pages/community/NewTopicPage';
import MyPage from './pages/my/MyPage';
import ProfileEditPage from './pages/my/ProfileEditPage';
import MyResourcesPage from './pages/my/MyResourcesPage';
import MyTopicsPage from './pages/my/MyTopicsPage';
import MyCollectionsPage from './pages/my/MyCollectionsPage';
import BeansDetailPage from './pages/my/BeansDetailPage';
import CreditDetailPage from './pages/my/CreditDetailPage';
import LevelPage from './pages/my/LevelPage';
import AccountSecurityPage from './pages/my/AccountSecurityPage';
import SearchPage from './pages/search/SearchPage';
import NotificationPage from './pages/notification/NotificationPage';
import FeedbackPage from './pages/feedback/FeedbackPage';
import SettingsPage from './pages/settings/SettingsPage';
import InvitePage from './pages/invite/InvitePage';

const AuthInitializer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const init = useAuthStore((s: any) => s.init);
  useEffect(() => {
    init();
  }, [init]);
  return <>{children}</>;
};

export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <AuthInitializer>
        <PhoneFrame />
      </AuthInitializer>
    ),
    children: [
      { index: true, element: <Navigate to="/welcome" replace /> },
      { path: 'welcome', element: <WelcomePage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'forgot-password', element: <ForgotPasswordPage /> },
      { path: 'profile-setup', element: <ProfileSetupPage /> },
      { path: 'ask', element: <AskPage /> },
      { path: 'chat/:sessionId?', element: <ChatPage /> },
      { path: 'resource', element: <ResourcePage /> },
      { path: 'resource/:id', element: <ResourceDetailPage /> },
      { path: 'resource/upload', element: <ResourceUploadPage /> },
      { path: 'resource/category/:category', element: <ResourceCategoryPage /> },
      { path: 'community', element: <CommunityPage /> },
      { path: 'community/topic/:id', element: <TopicDetailPage /> },
      { path: 'community/category/:category', element: <CommunityCategoryPage /> },
      { path: 'community/new-topic', element: <NewTopicPage /> },
      { path: 'my', element: <MyPage /> },
      { path: 'my/profile-edit', element: <ProfileEditPage /> },
      { path: 'my/resources', element: <MyResourcesPage /> },
      { path: 'my/topics', element: <MyTopicsPage /> },
      { path: 'my/collections', element: <MyCollectionsPage /> },
      { path: 'my/beans', element: <BeansDetailPage /> },
      { path: 'my/credit', element: <CreditDetailPage /> },
      { path: 'my/level', element: <LevelPage /> },
      { path: 'my/security', element: <AccountSecurityPage /> },
      { path: 'search', element: <SearchPage /> },
      { path: 'notification', element: <NotificationPage /> },
      { path: 'feedback', element: <FeedbackPage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: 'invite', element: <InvitePage /> },
    ],
  },
]);
