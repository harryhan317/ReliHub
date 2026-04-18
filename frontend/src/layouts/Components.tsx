import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useUIStore } from '../store/uiStore';
import { Modal } from '../components/ui/Modal';

interface TopBarProps {
  title?: React.ReactNode;
  onBack?: () => void;
  rightContent?: React.ReactNode;
  leftContent?: React.ReactNode;
  transparent?: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({ title, onBack, rightContent, leftContent, transparent }) => {
  const navigate = useNavigate();

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      navigate(-1);
    }
  };

  return (
    <div className="top-bar" style={transparent ? { background: 'transparent', border: 'none' } : undefined}>
      {leftContent || <button className="top-bar-btn" onClick={handleBack}>←</button>}
      <div className="top-bar-title">{title}</div>
      {rightContent || <div style={{ width: 32 }} />}
    </div>
  );
};

interface TopBarCustomProps {
  children: React.ReactNode;
  transparent?: boolean;
}

export const TopBarCustom: React.FC<TopBarCustomProps> = ({ children, transparent }) => {
  return (
    <div className="top-bar" style={transparent ? { background: 'transparent', border: 'none' } : undefined}>
      {children}
    </div>
  );
};

interface BottomNavProps {
  activeTab: string;
}

export const BottomNav: React.FC<BottomNavProps> = ({ activeTab }) => {
  const navigate = useNavigate();
  const { isGuest } = useAuthStore();
  const { showToast } = useUIStore();

  const handleTabClick = (tab: string) => {
    if (tab === 'my' && isGuest) {
      showToast('请先登录以查看个人中心', 'info');
      navigate('/login');
      return;
    }

    const routeMap: Record<string, string> = {
      ask: '/ask',
      resource: '/resource',
      community: '/community',
      my: '/my',
    };

    navigate(routeMap[tab] || '/');
  };

  const tabs = [
    { key: 'ask', icon: '🤖', label: '爱问' },
    { key: 'resource', icon: '📚', label: '资源' },
    { key: 'community', icon: '💬', label: '社区' },
    { key: 'my', icon: '👤', label: '我的' },
  ];

  return (
    <div className="bottom-nav">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          className={`nav-item ${activeTab === tab.key ? 'active' : ''}`}
          onClick={() => handleTabClick(tab.key)}
        >
          <span className="nav-icon">{tab.icon}</span>
          <span className="nav-label">{tab.label}</span>
        </button>
      ))}
    </div>
  );
};

interface GuestBannerProps {
  icon?: string;
  text: string;
  actionText?: string;
  onAction?: () => void;
  onRegister?: () => void;
}

export const GuestBanner: React.FC<GuestBannerProps> = ({ icon = '👋', text, actionText = '注册', onAction, onRegister }) => {
  const { isGuest } = useAuthStore();
  const navigate = useNavigate();

  if (!isGuest) return null;

  return (
    <div className="guest-banner">
      <span className="guest-banner-icon">{icon}</span>
      <span className="guest-banner-text">{text}</span>
      <span
        className="guest-banner-btn"
        onClick={() => {
          if (onAction) onAction();
          else if (onRegister) onRegister();
          else navigate('/login');
        }}
      >
        {actionText}
      </span>
    </div>
  );
};

interface SearchBarProps {
  placeholder: string;
  onSearch: () => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({ placeholder, onSearch }) => {
  return (
    <div className="search-bar">
      <div className="search-input-wrapper" style={{ cursor: 'pointer' }} onClick={onSearch}>
        <span className="search-icon">🔍</span>
        <input type="text" placeholder={placeholder} readOnly style={{ cursor: 'pointer' }} />
      </div>
    </div>
  );
};

interface SectionHeaderProps {
  title: string;
  action?: string;
  onAction?: () => void;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({ title, action, onAction }) => {
  return (
    <div className="section-header">
      <div className="section-title">{title}</div>
      {action && (
        <span className="section-action" onClick={onAction}>{action}</span>
      )}
    </div>
  );
};

interface TabBarProps {
  tabs: string[];
  activeIndex: number;
  onTabChange: (index: number) => void;
}

export const TabBar: React.FC<TabBarProps> = ({ tabs, activeIndex, onTabChange }) => {
  const width = 100 / tabs.length;

  return (
    <div className="tab-bar">
      {tabs.map((tab, index) => (
        <button
          key={tab}
          className={`tab-item ${index === activeIndex ? 'active' : ''}`}
          onClick={() => onTabChange(index)}
        >
          {tab}
        </button>
      ))}
      <div
        className="tab-indicator"
        style={{ left: `${activeIndex * width}%`, width: `${width}%` }}
      />
    </div>
  );
};

interface RegisterGuideProps {
  open: boolean;
  onClose: () => void;
}

export const RegisterGuide: React.FC<RegisterGuideProps> = ({ open, onClose }) => {
  const navigate = useNavigate();

  const benefits = [
    { icon: '✅', text: '无限AI对话，专业可靠性问答' },
    { icon: '✅', text: '下载海量专业资源' },
    { icon: '✅', text: '参与社区讨论，悬赏互动' },
    { icon: '✅', text: '签到赚可可豆，提升信誉' },
  ];

  return (
    <Modal open={open} onClose={onClose}>
      <div className="register-guide-content">
        <div className="register-guide-title">加入 ReliHub</div>
        <div className="early-bird-badge">🌟 早鸟福利 · 注册即得50🫘</div>
        <div className="register-guide-benefits">
          {benefits.map((b) => (
            <div key={b.text} className="benefit-item">
              <span className="benefit-icon">{b.icon}</span>
              <span className="benefit-text">{b.text}</span>
            </div>
          ))}
        </div>
        <button className="btn btn-primary btn-block btn-lg" onClick={() => { onClose(); navigate('/login'); }}>
          立即注册
        </button>
        <div
          style={{ marginTop: 'var(--spacing-md)', fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)', cursor: 'pointer', textAlign: 'center' }}
          onClick={onClose}
        >
          继续浏览
        </div>
      </div>
    </Modal>
  );
};
