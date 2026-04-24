import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { TopBar } from '../../layouts/Components';

const ProfileSetupPage: React.FC = () => {
  const navigate = useNavigate();
  const { updateUser, user } = useAuthStore();
  const { showToast } = useUIStore();
  const [nickname, setNickname] = useState(user?.nickname || '');
  const [gender, setGender] = useState('');
  const [company, setCompany] = useState(user?.company || '');
  const [position, setPosition] = useState(user?.position || '');
  const [email, setEmail] = useState(user?.email || '');

  const handleSave = () => {
    if (!nickname) { showToast('请输入昵称', 'error'); return; }
    updateUser({ nickname, company, position, email, gender });
    showToast('资料设置成功', 'success');
    navigate('/ask');
  };

  return (
    <div className="page active">
      <TopBar title="完善个人档案" leftContent={
        <button className="top-bar-btn" onClick={() => navigate('/ask')}>跳过</button>
      } />
      <div className="profile-setup">
        <div className="profile-avatar-upload">
          <div className="profile-avatar-circle">😊</div>
          <span style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-accent)' }}>点击上传头像</span>
        </div>
        <div className="profile-form">
          <div className="input-group">
            <label className="input-label">昵称<span className="required-mark">*</span></label>
            <input className="input-field" type="text" placeholder="给自己取个名字吧" maxLength={20} value={nickname} onChange={(e) => setNickname(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">性别<span className="optional-mark">选填</span></label>
            <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
              <button className={`btn ${gender === '男' ? 'btn-primary' : 'btn-secondary'} btn-sm`} style={{ flex: 1 }} onClick={() => setGender(gender === '男' ? '' : '男')}>男</button>
              <button className={`btn ${gender === '女' ? 'btn-primary' : 'btn-secondary'} btn-sm`} style={{ flex: 1 }} onClick={() => setGender(gender === '女' ? '' : '女')}>女</button>
            </div>
          </div>
          <div className="input-group">
            <label className="input-label">单位<span className="optional-mark">选填</span></label>
            <input className="input-field" type="text" placeholder="公司或机构名称" value={company} onChange={(e) => setCompany(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">职务<span className="optional-mark">选填</span></label>
            <input className="input-field" type="text" placeholder="如：质量工程师" value={position} onChange={(e) => setPosition(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">Email<span className="optional-mark">选填</span></label>
            <input className="input-field" type="email" placeholder="your@email.com" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <button className="btn btn-primary btn-block btn-lg" onClick={handleSave} style={{ marginTop: 'var(--spacing-md)' }}>完成</button>
        </div>
      </div>
    </div>
  );
};

export default ProfileSetupPage;
