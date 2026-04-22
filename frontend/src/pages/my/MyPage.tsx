import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { useGuestGuard } from '../../store/useGuestGuard';
import { BottomNav } from '../../layouts/Components';
import { Avatar } from '../../components/ui/Common';
import { Modal } from '../../components/ui/Modal';
import { GuestRegisterModal } from '../../components/ui/GuestRegisterModal';
import { ledgerService } from '../../services/otherServices';

const MyPage: React.FC = () => {
  const navigate = useNavigate();
  const { isGuest, isLoggedIn, user, logout } = useAuthStore();
  const { showToast } = useUIStore();
  const { checkAction, guideModal, closeGuideModal } = useGuestGuard();
  const [checkedIn, setCheckedIn] = useState(user?.checked_in_today || false);
  const [showCheckin, setShowCheckin] = useState(false);
  const [showLogout, setShowLogout] = useState(false);

  const streakDays = [
    { label: '一', checked: true },
    { label: '二', checked: true },
    { label: '三', checked: true },
    { label: '四', checked: false, today: true },
    { label: '五', checked: false },
    { label: '六', checked: false },
    { label: '日', checked: false },
  ];

  const handleCheckin = async () => {
    if (isGuest) { checkAction('open_my'); return; }
    try {
      const res: any = await ledgerService.checkin();
      if (res?.already_checked_in) {
        setCheckedIn(true);
        showToast('今日已签到', 'info');
      } else {
        setCheckedIn(true);
        setShowCheckin(true);
        showToast('签到成功！', 'success');
      }
    } catch (err: any) {
      showToast(err?.message || '签到失败，请稍后重试', 'error');
    }
  };

  const menuItems = [
    { icon: '📚', label: '我的资源', color: 'var(--color-accent-light)', route: '/my/resources' },
    { icon: '💬', label: '我的话题', color: 'rgba(16,185,129,0.15)', route: '/my/topics' },
    { icon: '⭐', label: '我的收藏', color: 'rgba(245,158,11,0.15)', route: '/my/collections' },
    { icon: '🔔', label: '消息通知', color: 'rgba(239,68,68,0.15)', route: '/notification' },
    { icon: '📝', label: '意见反馈', color: 'rgba(139,92,246,0.15)', route: '/feedback' },
    { icon: '🎁', label: '邀请好友', color: 'rgba(59,130,246,0.15)', route: '/invite' },
    { icon: '⚙️', label: '设置', color: 'rgba(100,116,139,0.15)', route: '/settings' },
  ];

  return (
    <div className="page active">
      <div className="top-bar">
        <div className="top-bar-title">我的</div>
        <button className="top-bar-btn" onClick={() => navigate('/settings')}>⚙️</button>
      </div>
      <div className="content-area">
        <div style={{ padding: 'var(--spacing-lg)', display: 'flex', alignItems: 'center', gap: 'var(--spacing-lg)', marginBottom: 'var(--spacing-md)' }}>
          <Avatar size="lg">{isGuest ? '😊' : (user?.nickname?.[0] || '😊')}</Avatar>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 600 }}>
              {isGuest ? '点击登录' : (user?.nickname || '用户')}
            </div>
            <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-tertiary)', marginTop: 2 }}>
              {isGuest ? '登录后享受完整功能' : (user?.company || user?.level || '')}
            </div>
          </div>
          {isGuest ? (
            <button className="btn btn-primary btn-sm" onClick={() => navigate('/login')}>登录/注册</button>
          ) : (
            <button className="top-bar-btn" onClick={() => navigate('/my/profile-edit')}>✏️</button>
          )}
        </div>

        <div style={{ display: 'flex', gap: 'var(--spacing-md)', padding: '0 var(--spacing-lg)', marginBottom: 'var(--spacing-lg)' }}>
          <div className="stat-card" style={{ cursor: 'pointer' }} onClick={() => navigate('/my/beans')}>
            <div className="stat-value" style={{ color: 'var(--color-gold)' }}>{user?.cocoa_beans || 0}</div>
            <div className="stat-label">🫘 可可豆</div>
          </div>
          <div className="stat-card" style={{ cursor: 'pointer' }} onClick={() => navigate('/my/credit')}>
            <div className="stat-value" style={{ color: 'var(--color-accent)' }}>{user?.credit_score || '--'}</div>
            <div className="stat-label">⭐ 信誉分</div>
          </div>
          <div className="stat-card" style={{ cursor: 'pointer' }} onClick={() => navigate('/my/level')}>
            <div className="stat-value">{user?.topic_count || 0}</div>
            <div className="stat-label">📝 话题</div>
          </div>
        </div>

        <div className="checkin-card">
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 600, marginBottom: 'var(--spacing-sm)' }}>📅 每日签到</div>
          <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-tertiary)', marginBottom: 'var(--spacing-md)' }}>
            签到可获得可可豆和信誉分奖励
          </div>
          <div className="checkin-streak">
            {streakDays.map((day) => (
              <div key={day.label} className={`streak-day ${day.checked ? 'checked' : ''} ${day.today ? 'today' : ''}`}>
                {day.label}
              </div>
            ))}
          </div>
          <button
            className="btn btn-primary btn-sm"
            onClick={handleCheckin}
            disabled={checkedIn}
            style={{ opacity: checkedIn ? 0.6 : 1 }}
          >
            {checkedIn ? '已签到 ✓' : '签到 +2🫘'}
          </button>
        </div>

        <div style={{ marginTop: 'var(--spacing-md)' }}>
          {menuItems.map((item, i) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.03 }}
            >
              <div className="menu-item" onClick={() => navigate(item.route)}>
                <div className="menu-icon" style={{ background: item.color }}>{item.icon}</div>
                <span className="menu-text">{item.label}</span>
                <span className="menu-arrow">›</span>
              </div>
            </motion.div>
          ))}
        </div>

        {isLoggedIn && (
          <div style={{ padding: 'var(--spacing-xl) var(--spacing-lg)' }}>
            <button className="btn btn-secondary btn-block" onClick={() => setShowLogout(true)}>退出登录</button>
          </div>
        )}
      </div>
      <BottomNav activeTab="my" />

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

      <Modal open={showCheckin} onClose={() => setShowCheckin(false)}>
        <div style={{ padding: 'var(--spacing-xl)', textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 'var(--spacing-md)' }}>🎉</div>
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 700, marginBottom: 'var(--spacing-sm)' }}>签到成功</div>
          <div style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-lg)' }}>
            获得 <span className="gradient-text" style={{ fontWeight: 700 }}>2 可可豆</span> 奖励
          </div>
          <button className="btn btn-primary btn-block" onClick={() => setShowCheckin(false)}>好的</button>
        </div>
      </Modal>

      <GuestRegisterModal
        open={guideModal.open}
        onClose={closeGuideModal}
        source={guideModal.source}
        reason={guideModal.reason}
      />
    </div>
  );
};

export default MyPage;
