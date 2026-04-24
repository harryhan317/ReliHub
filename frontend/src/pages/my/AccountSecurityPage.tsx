import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { TopBar } from '../../layouts/Components';
import { Modal } from '../../components/ui/Modal';
import { authService } from '../../services/authService';

const AccountSecurityPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { showToast } = useUIStore();
  const [showChangePwd, setShowChangePwd] = useState(false);
  const [oldPwd, setOldPwd] = useState('');
  const [newPwd, setNewPwd] = useState('');
  const [confirmPwd, setConfirmPwd] = useState('');
  const [showDelete, setShowDelete] = useState(false);

  const handleChangePwd = async () => {
    if (!oldPwd) { showToast('请输入旧密码', 'error'); return; }
    if (!newPwd) { showToast('请输入新密码', 'error'); return; }
    if (newPwd.length < 8 || newPwd.length > 20) { showToast('密码需8-20位', 'error'); return; }
    if (newPwd !== confirmPwd) { showToast('两次密码不一致', 'error'); return; }
    try {
      await authService.resetPassword(user?.phone || '', '', newPwd);
      showToast('密码修改成功', 'success');
      setShowChangePwd(false);
      setOldPwd('');
      setNewPwd('');
      setConfirmPwd('');
    } catch {
      showToast('密码修改失败', 'error');
    }
  };

  const handleDeleteAccount = () => {
    logout();
    navigate('/welcome');
    showToast('账号已注销', 'success');
  };

  return (
    <div className="page active">
      <TopBar title="账号安全" />
      <div className="content-area-no-nav">
        <div className="menu-item" onClick={() => setShowChangePwd(true)}>
          <div className="menu-icon" style={{ background: 'var(--color-accent-light)' }}>🔑</div>
          <div className="menu-text">修改密码</div>
          <span className="menu-arrow">›</span>
        </div>
        <div className="menu-item" onClick={() => navigate('/my/profile-edit')}>
          <div className="menu-icon" style={{ background: 'rgba(16,185,129,0.15)' }}>📱</div>
          <div className="menu-text">绑定手机号</div>
          <span style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)', marginRight: 'var(--spacing-sm)' }}>{user?.phone ? user.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '未绑定'}</span>
          <span className="menu-arrow">›</span>
        </div>
        <div className="divider"></div>
        <div className="menu-item">
          <div className="menu-icon" style={{ background: 'rgba(245,158,11,0.15)' }}>🖥️</div>
          <div className="menu-text">登录设备管理</div>
          <span className="menu-arrow">›</span>
        </div>
        <div className="menu-item">
          <div className="menu-icon" style={{ background: 'rgba(239,68,68,0.15)' }}>⚠️</div>
          <div className="menu-text">异常登录记录</div>
          <span className="menu-arrow">›</span>
        </div>
        <div className="divider"></div>
        <div style={{ padding: 'var(--spacing-xl)' }}>
          <button className="btn btn-secondary btn-block" style={{ color: 'var(--color-error)', borderColor: 'rgba(239,68,68,0.3)' }} onClick={() => setShowDelete(true)}>注销账号</button>
          <div style={{ textAlign: 'center', fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-sm)' }}>注销后数据不可恢复</div>
        </div>
      </div>

      <Modal open={showChangePwd} onClose={() => setShowChangePwd(false)}>
        <div style={{ padding: 'var(--spacing-xl)' }}>
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 700, marginBottom: 'var(--spacing-lg)', textAlign: 'center' }}>修改密码</div>
          <div className="input-group">
            <label className="input-label">旧密码</label>
            <input className="input-field" type="password" placeholder="请输入旧密码" value={oldPwd} onChange={(e) => setOldPwd(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">新密码</label>
            <input className="input-field" type="password" placeholder="8-20位，含大小写/数字/特殊符号至少2项" value={newPwd} onChange={(e) => setNewPwd(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">确认新密码</label>
            <input className="input-field" type="password" placeholder="再次输入新密码" value={confirmPwd} onChange={(e) => setConfirmPwd(e.target.value)} />
          </div>
          <div style={{ display: 'flex', gap: 'var(--spacing-md)', marginTop: 'var(--spacing-lg)' }}>
            <button className="btn btn-secondary btn-block" onClick={() => setShowChangePwd(false)}>取消</button>
            <button className="btn btn-primary btn-block" onClick={handleChangePwd}>确认修改</button>
          </div>
        </div>
      </Modal>

      <Modal open={showDelete} onClose={() => setShowDelete(false)}>
        <div style={{ padding: 'var(--spacing-xl)', textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 'var(--spacing-md)' }}>⚠️</div>
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 700, marginBottom: 'var(--spacing-sm)' }}>确认注销账号</div>
          <div style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xl)', lineHeight: 'var(--line-height-body)' }}>
            注销后所有数据将不可恢复，包括可可豆、信誉分、对话记录、资源、话题等。
          </div>
          <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
            <button className="btn btn-secondary btn-block" onClick={() => setShowDelete(false)}>再想想</button>
            <button className="btn btn-primary btn-block" style={{ background: 'var(--color-error)' }} onClick={handleDeleteAccount}>确认注销</button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default AccountSecurityPage;
