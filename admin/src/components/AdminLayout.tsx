import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useAdminStore } from '@/store/adminStore';

const navItems = [
  {
    section: '概览',
    items: [
      { path: '/admin/dashboard', icon: '📊', label: '系统看板' },
    ],
  },
  {
    section: '配置管理',
    items: [
      { path: '/admin/config-ai', icon: '🤖', label: 'AI问答配置' },
      { path: '/admin/config-level', icon: '🏆', label: '等级体系' },
      { path: '/admin/config-beans', icon: '🫘', label: '可可豆/信誉分' },
      { path: '/admin/config-category', icon: '📂', label: '分类管理' },
      { path: '/admin/config-security', icon: '🔒', label: '安全风控' },
    ],
  },
  {
    section: '内容管理',
    items: [
      { path: '/admin/audit-resource', icon: '📋', label: '资源审核' },
      { path: '/admin/audit-community', icon: '💬', label: '社区审核' },
    ],
  },
  {
    section: '用户管理',
    items: [
      { path: '/admin/user-list', icon: '👥', label: '用户列表' },
      { path: '/admin/user-expert', icon: '🎓', label: '专家认证' },
    ],
  },
];

const pageTitles: Record<string, string> = {
  dashboard: '系统看板',
  'config-ai': 'AI问答配置',
  'config-level': '等级体系配置',
  'config-beans': '可可豆/信誉分配置',
  'config-category': '分类管理',
  'config-security': '安全风控配置',
  'audit-resource': '资源审核',
  'audit-community': '社区审核',
  'user-list': '用户列表',
  'user-expert': '专家认证审核',
};

export default function AdminLayout() {
  const location = useLocation();
  const { adminUser, logout } = useAdminStore();
  const pageKey = location.pathname.split('/').pop() || 'dashboard';
  const pageTitle = pageTitles[pageKey] || pageKey;
  const roleLabel = adminUser?.role === 'SUPER_ADMIN' ? '超级管理员' : adminUser?.role === 'OPERATOR' ? '运营管理员' : '审计员';
  const avatarText = adminUser?.role === 'SUPER_ADMIN' ? 'SA' : adminUser?.username?.slice(0, 2)?.toUpperCase() || 'AD';

  return (
    <div className="admin-layout">
      <div className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">R</div>
          <div className="sidebar-logo-text">ReliHub</div>
          <div className="sidebar-logo-badge">Admin</div>
        </div>
        {navItems.map((group) => (
          <div className="sidebar-section" key={group.section}>
            <div className="sidebar-section-title">{group.section}</div>
            {group.items.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => `sidebar-item${isActive ? ' active' : ''}`}
              >
                <span className="sidebar-item-icon">{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </div>
        ))}
      </div>

      <div className="main">
        <div className="header">
          <div className="header-left">
            <div className="header-breadcrumb">
              ReliHub / <span>{pageTitle}</span>
            </div>
          </div>
          <div className="header-right">
            <span style={{ fontSize: 13, color: 'var(--admin-text-muted)' }}>{roleLabel}</span>
            <div className="header-avatar">{avatarText}</div>
            <span className="header-username">{adminUser?.username || 'Admin'}</span>
            <button className="btn btn-sm" onClick={logout} style={{ marginLeft: 8 }}>退出</button>
          </div>
        </div>

        <div className="content">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
