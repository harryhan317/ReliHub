import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { TopBar } from '../../layouts/Components';
import { Card } from '../../components/ui/Common';

const InvitePage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { showToast } = useUIStore();

  const inviteCode = 'RELI2026';

  return (
    <div className="page active">
      <TopBar title="邀请好友" />
      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-xl)', textAlign: 'center' }}>
        <div style={{ fontSize: 48, marginBottom: 'var(--spacing-lg)' }}>🎁</div>
        <div style={{ fontSize: 'var(--font-size-h2)', fontWeight: 700, marginBottom: 'var(--spacing-sm)' }}>邀请好友，各得10🫘</div>
        <div style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-tertiary)', marginBottom: 'var(--spacing-xl)', lineHeight: 'var(--line-height-body)' }}>
          每成功邀请一位好友注册并完善个人档案，你和好友各获得10个可可豆奖励
        </div>
        <Card style={{ marginBottom: 'var(--spacing-xl)' }}>
          <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-sm)' }}>我的邀请码</div>
          <div style={{ fontSize: 'var(--font-size-h2)', fontWeight: 700, letterSpacing: 4, color: 'var(--color-accent)' }}>{inviteCode}</div>
          <button className="btn btn-primary btn-sm" style={{ marginTop: 'var(--spacing-md)' }} onClick={() => { navigator.clipboard.writeText(inviteCode); showToast('邀请码已复制', 'success'); }}>
            复制邀请码
          </button>
        </Card>
        <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
          <button className="btn btn-wechat" style={{ flex: 1 }}>💬 微信分享</button>
          <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => { navigator.clipboard.writeText(`https://relihub.com/invite/${inviteCode}`); showToast('链接已复制', 'success'); }}>🔗 复制链接</button>
        </div>
        <div style={{ marginTop: 'var(--spacing-xl)', fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)' }}>
          已邀请 <strong style={{ color: 'var(--color-accent)' }}>3</strong> 位好友 · 获得 <strong style={{ color: 'var(--color-gold)' }}>30</strong> 🫘
        </div>
      </div>
    </div>
  );
};

export default InvitePage;
