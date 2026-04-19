import { Routes, Route, Navigate } from 'react-router-dom';
import { useAdminStore } from '@/store/adminStore';
import { useEffect } from 'react';
import AdminLayout from '@/components/AdminLayout';
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/dashboard/DashboardPage';
import ConfigAIPage from '@/pages/config/ConfigAIPage';
import ConfigLevelPage from '@/pages/config/ConfigLevelPage';
import ConfigBeansPage from '@/pages/config/ConfigBeansPage';
import ConfigCategoryPage from '@/pages/config/ConfigCategoryPage';
import ConfigSecurityPage from '@/pages/config/ConfigSecurityPage';
import AuditResourcePage from '@/pages/content/AuditResourcePage';
import AuditCommunityPage from '@/pages/content/AuditCommunityPage';
import UserListPage from '@/pages/users/UserListPage';
import UserExpertPage from '@/pages/users/UserExpertPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn } = useAdminStore();
  if (!isLoggedIn) return <Navigate to="/admin/login" replace />;
  return <>{children}</>;
}

export default function App() {
  const init = useAdminStore((s) => s.init);

  useEffect(() => {
    init();
  }, [init]);

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
        <Route path="config-level" element={<ConfigLevelPage />} />
        <Route path="config-beans" element={<ConfigBeansPage />} />
        <Route path="config-category" element={<ConfigCategoryPage />} />
        <Route path="config-security" element={<ConfigSecurityPage />} />
        <Route path="audit-resource" element={<AuditResourcePage />} />
        <Route path="audit-community" element={<AuditCommunityPage />} />
        <Route path="user-list" element={<UserListPage />} />
        <Route path="user-expert" element={<UserExpertPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/admin" replace />} />
    </Routes>
  );
}
