import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUIStore } from '../../store/uiStore';
import { TopBar } from '../../layouts/Components';

const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const { showToast } = useUIStore();
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [countdown, setCountdown] = useState(0);

  const handleSendCode = () => {
    if (!phone) { showToast('请输入手机号', 'error'); return; }
    setCountdown(60);
    const timer = setInterval(() => {
      setCountdown((prev) => { if (prev <= 1) { clearInterval(timer); return 0; } return prev - 1; });
    }, 1000);
    showToast('验证码已发送', 'success');
  };

  const handleReset = () => {
    if (!phone || !code || !newPassword) { showToast('请填写完整信息', 'error'); return; }
    if (newPassword !== confirmPassword) { showToast('两次密码不一致', 'error'); return; }
    showToast('密码重置成功', 'success');
    navigate('/login');
  };

  return (
    <div className="page active">
      <TopBar title="重置密码" />
      <div style={{ padding: 'var(--spacing-xl)', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-lg)' }}>
        <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-tertiary)', marginBottom: 'var(--spacing-md)' }}>通过手机验证码验证身份后重置密码</div>
        <div className="input-group">
          <div className="phone-input-row">
            <span className="phone-prefix">+86</span>
            <input className="input-field" type="tel" placeholder="请输入注册手机号" maxLength={11} value={phone} onChange={(e) => setPhone(e.target.value)} />
          </div>
        </div>
        <div className="input-group">
          <div className="code-input-row">
            <input className="input-field" type="text" placeholder="请输入验证码" maxLength={6} value={code} onChange={(e) => setCode(e.target.value)} />
            <button className="send-code-btn" onClick={handleSendCode} disabled={countdown > 0} style={{ opacity: countdown > 0 ? 0.5 : 1 }}>
              {countdown > 0 ? `${countdown}s` : '获取验证码'}
            </button>
          </div>
        </div>
        <div className="input-group">
          <label className="input-label">新密码</label>
          <input className="input-field" type="password" placeholder="8-20位，含大小写字母/数字/符号至少2种" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
        </div>
        <div className="input-group">
          <label className="input-label">确认密码</label>
          <input className="input-field" type="password" placeholder="请再次输入新密码" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
        </div>
        <button className="btn btn-primary btn-block btn-lg" onClick={handleReset} style={{ marginTop: 'var(--spacing-md)' }}>确认重置</button>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
