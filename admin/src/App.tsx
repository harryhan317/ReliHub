import { Routes, Route, Navigate } from 'react-router-dom';
import { useAdminStore } from '@/store/adminStore';
import { useEffect, useState } from 'react';
import AdminLayout from '@/components/AdminLayout';
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/dashboard/DashboardPage';
import ConfigAIPage from '@/pages/config/ConfigAIPage';
import ConfigAIModelPage from '@/pages/config/ConfigAIModelPage';
import ConfigLevelPage from '@/pages/config/ConfigLevelPage';
import ConfigPermissionPage from '@/pages/config/ConfigPermissionPage';
import ConfigBeansPage from '@/pages/config/ConfigBeansPage';
import ConfigCategoryPage from '@/pages/config/ConfigCategoryPage';
import ConfigDownloadPackPage from '@/pages/config/ConfigDownloadPackPage';
import ConfigSecurityPage from '@/pages/config/ConfigSecurityPage';
import ConfigFileFormatPage from '@/pages/config/ConfigFileFormatPage';
import ConfigProfileRequiredPage from '@/pages/config/ConfigProfileRequiredPage';
import ConfigSensitiveWordPage from '@/pages/config/ConfigSensitiveWordPage';
import ConfigPricingPage from '@/pages/config/ConfigPricingPage';
import AuditResourcePage from '@/pages/content/AuditResourcePage';
import AuditCommunityPage from '@/pages/content/AuditCommunityPage';
import UserListPage from '@/pages/users/UserListPage';
import UserExpertPage from '@/pages/users/UserExpertPage';
import FeedbackPage from '@/pages/users/FeedbackPage';
import AdminAccountPage from '@/pages/users/AdminAccountPage';
import SecurityLogPage from '@/pages/security/SecurityLogPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn, init } = useAdminStore();
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    init();
    setInitialized(true);
  }, [init]);

  if (!initialized) return null;
  if (!isLoggedIn) return <Navigate to="/admin/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/admin/login" element={<LoginPage />} />
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="config-ai" element={<ConfigAIPage />} />
        <Route path="config-ai-model" element={<ConfigAIModelPage />} />
        <Route path="config-level" element={<ConfigLevelPage />} />
        <Route path="config-permission" element={<ConfigPermissionPage />} />
        <Route path="config-beans" element={<ConfigBeansPage />} />
        <Route path="config-category" element={<ConfigCategoryPage />} />
        <Route path="config-download-pack" element={<ConfigDownloadPackPage />} />
        <Route path="config-file-format" element={<ConfigFileFormatPage />} />
        <Route path="config-profile-required" element={<ConfigProfileRequiredPage />} />
        <Route path="config-sensitive-word" element={<ConfigSensitiveWordPage />} />
        <Route path="config-pricing" element={<ConfigPricingPage />} />
        <Route path="config-security" element={<ConfigSecurityPage />} />
        <Route path="audit-resource" element={<AuditResourcePage />} />
        <Route path="audit-community" element={<AuditCommunityPage />} />
        <Route path="user-list" element={<UserListPage />} />
        <Route path="user-expert" element={<UserExpertPage />} />
        <Route path="feedback" element={<FeedbackPage />} />
        <Route path="admin-account" element={<AdminAccountPage />} />
        <Route path="security-log" element={<SecurityLogPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/admin" replace />} />
    </Routes>
  );
}
