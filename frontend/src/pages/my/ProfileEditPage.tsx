import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { TopBar } from '../../layouts/Components';

const ProfileEditPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, updateUser } = useAuthStore();
  const { showToast } = useUIStore();
  const [nickname, setNickname] = useState(user?.nickname || '可靠性工程师');
  const [gender, setGender] = useState(user?.gender || '男');
  const [company, setCompany] = useState(user?.company || '某科技公司');
  const [position, setPosition] = useState(user?.position || '质量工程师');
  const [email, setEmail] = useState(user?.email || 'engineer@example.com');

  const handleSave = () => {
    if (!nickname) { showToast('昵称不能为空', 'error'); return; }
    updateUser({ nickname, company, position, email, gender });
    showToast('资料更新成功', 'success');
    navigate(-1);
  };

  return (
    <div className="page active">
      <TopBar title="编辑资料" rightContent={
        <button className="top-bar-btn" onClick={handleSave} style={{ color: 'var(--color-accent)', fontWeight: 600, fontSize: 'var(--font-size-body)' }}>保存</button>
      } />
      <div className="content-area-no-nav">
        <div style={{ padding: 'var(--spacing-xl)' }}>
          <div className="profile-avatar-upload">
            <div className="profile-avatar-circle">😊</div>
            <span style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-accent)' }}>更换头像</span>
          </div>
          <div className="profile-form">
            <div className="input-group">
              <label className="input-label">昵称<span className="required-mark">*</span></label>
              <input className="input-field" type="text" value={nickname} maxLength={20} onChange={(e) => setNickname(e.target.value)} />
            </div>
            <div className="input-group">
              <label className="input-label">性别</label>
              <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
                <button className={`btn ${gender === '男' ? 'btn-primary' : 'btn-secondary'} btn-sm`} style={{ flex: 1 }} onClick={() => setGender('男')}>男</button>
                <button className={`btn ${gender === '女' ? 'btn-primary' : 'btn-secondary'} btn-sm`} style={{ flex: 1 }} onClick={() => setGender('女')}>女</button>
              </div>
            </div>
            <div className="input-group">
              <label className="input-label">单位</label>
              <input className="input-field" type="text" value={company} onChange={(e) => setCompany(e.target.value)} />
            </div>
            <div className="input-group">
              <label className="input-label">职务</label>
              <input className="input-field" type="text" value={position} onChange={(e) => setPosition(e.target.value)} />
            </div>
            <div className="input-group">
              <label className="input-label">Email</label>
              <input className="input-field" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileEditPage;
