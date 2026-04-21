import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { TopBar } from '../../layouts/Components';
import { Switch } from '../../components/ui/Common';
import { Modal } from '../../components/ui/Modal';

const SettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const { logout, isLoggedIn } = useAuthStore();
  const { showToast } = useUIStore();
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [showLogout, setShowLogout] = useState(false);

  return (
    <div className="page active">
      <TopBar title="设置" />
      <div className="content-area-no-nav">
        <div className="menu-item" onClick={() => navigate('/my/profile-edit')}>
          <div className="menu-icon" style={{ background: 'var(--color-accent-light)' }}>👤</div>
          <div className="menu-text">个人资料</div>
          <span className="menu-arrow">›</span>
        </div>
        <div className="menu-item" onClick={() => navigate('/my/security')}>
          <div className="menu-icon" style={{ background: 'rgba(16,185,129,0.15)' }}>🔒</div>
          <div className="menu-text">账号安全</div>
          <span className="menu-arrow">›</span>
        </div>
        <div className="divider"></div>
        <div className="menu-item">
          <div className="menu-icon" style={{ background: 'rgba(245,158,11,0.15)' }}>🔔</div>
          <div className="menu-text">通知设置</div>
          <Switch on={notifications} onToggle={() => setNotifications(!notifications)} />
        </div>
        <div className="menu-item">
          <div className="menu-icon" style={{ background: 'rgba(139,92,246,0.15)' }}>🌙</div>
          <div className="menu-text">深色模式</div>
          <Switch on={darkMode} onToggle={() => { setDarkMode(!darkMode); showToast('深色模式开发中', 'info'); }} />
        </div>
        <div className="divider"></div>
        <div className="menu-item">
          <div className="menu-icon" style={{ background: 'rgba(59,130,246,0.15)' }}>📖</div>
          <div className="menu-text">用户协议</div>
          <span className="menu-arrow">›</span>
        </div>
        <div className="menu-item">
          <div className="menu-icon" style={{ background: 'rgba(100,116,139,0.15)' }}>🔒</div>
          <div className="menu-text">隐私政策</div>
          <span className="menu-arrow">›</span>
        </div>
        <div className="menu-item">
          <div className="menu-icon" style={{ background: 'rgba(100,116,139,0.15)' }}>ℹ️</div>
          <div className="menu-text">关于 ReliHub</div>
          <span className="menu-arrow">›</span>
        </div>
        <div className="divider"></div>
        <div style={{ padding: 'var(--spacing-xl)' }}>
          {isLoggedIn ? (
            <button className="btn btn-secondary btn-block" style={{ color: 'var(--color-error)', borderColor: 'rgba(239,68,68,0.3)' }} onClick={() => setShowLogout(true)}>退出登录</button>
          ) : (
            <button className="btn btn-primary btn-block" onClick={() => navigate('/login')}>登录</button>
          )}
          <div style={{ textAlign: 'center', fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-md)' }}>ReliHub v1.0.0 (MVP)</div>
        </div>
      </div>

      <Modal open={showLogout} onClose={() => setShowLogout(false)}>
        <div style={{ padding: 'var(--spacing-xl)', textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 'var(--spacing-md)' }}>👋</div>
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 700, marginBottom: 'var(--spacing-sm)' }}>确认退出</div>
          <div style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xl)' }}>
            退出后需要重新登录
          </div>
          <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
            <button className="btn btn-secondary btn-block" onClick={() => setShowLogout(false)}>取消</button>
            <button className="btn btn-primary btn-block" onClick={() => { logout(); navigate('/welcome'); }}>确认退出</button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default SettingsPage;
