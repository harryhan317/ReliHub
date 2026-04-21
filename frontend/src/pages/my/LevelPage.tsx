import React from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar } from '../../layouts/Components';
import { useAuthStore } from '../../store/authStore';

const levels = [
  { name: '新兵', min: 0, max: 99, icon: '🔰', benefits: ['浏览资源', 'AI问答(3次/天)', '社区浏览'] },
  { name: '菜鸟', min: 100, max: 299, icon: '🌱', benefits: ['下载资源', '发布话题', 'AI问答(5次/天)'] },
  { name: '入门', min: 300, max: 699, icon: '📈', benefits: ['上传资源', '回复话题', 'AI问答(10次/天)', '悬赏提问'] },
  { name: '熟手', min: 700, max: 1499, icon: '🔧', benefits: ['资源审核优先', 'AI问答(15次/天)', '社区投票'] },
  { name: '老炮', min: 1500, max: 2999, icon: '🎯', benefits: ['AI问答(20次/天)', '精华推荐权', '专属标识'] },
  { name: '达人', min: 3000, max: 5999, icon: '⭐', benefits: ['AI问答(30次/天)', '内容审核权', '达人徽章'] },
  { name: '专家', min: 6000, max: 99999, icon: '🏆', benefits: ['AI问答(无限)', '专家认证', '优先展示', '专属客服'] },
];

const LevelPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const currentLevel = user?.level || '新兵';
  const creditScore = user?.credit_score || 0;

  return (
    <div className="page active">
      <TopBar title="等级权益" />
      <div className="content-area-no-nav">
        <div style={{ padding: 'var(--spacing-xl)', textAlign: 'center', background: 'linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1))' }}>
          <div style={{ fontSize: 48 }}>{levels.find((l) => l.name === currentLevel)?.icon || '🔰'}</div>
          <div style={{ fontSize: 'var(--font-size-h2)', fontWeight: 700, color: 'var(--color-accent)', marginTop: 'var(--spacing-sm)' }}>{currentLevel}</div>
          <div style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-secondary)', marginTop: 4 }}>信誉分 {creditScore}</div>
        </div>

        <div style={{ padding: 'var(--spacing-lg)' }}>
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 600, marginBottom: 'var(--spacing-md)' }}>等级体系</div>
          {levels.map((level) => {
            const isCurrent = level.name === currentLevel;
            const isUnlocked = creditScore >= level.min;
            return (
              <div key={level.name} style={{
                padding: 'var(--spacing-md)',
                marginBottom: 'var(--spacing-sm)',
                borderRadius: 'var(--radius-lg)',
                background: isCurrent ? 'var(--color-accent-light)' : 'var(--color-bg-secondary)',
                border: isCurrent ? '2px solid var(--color-accent)' : '2px solid transparent',
                opacity: isUnlocked ? 1 : 0.6,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-xs)' }}>
                  <span style={{ fontSize: 20 }}>{level.icon}</span>
                  <span style={{ fontWeight: 600, fontSize: 'var(--font-size-body)' }}>{level.name}</span>
                  <span style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)' }}>{level.min}-{level.max} 分</span>
                  {isCurrent && <span style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-accent)', fontWeight: 600, marginLeft: 'auto' }}>当前</span>}
                  {isUnlocked && !isCurrent && <span style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-success)', marginLeft: 'auto' }}>✓ 已达成</span>}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-xs)' }}>
                  {level.benefits.map((b) => (
                    <span key={b} style={{ fontSize: 'var(--font-size-small)', padding: '2px 8px', background: 'rgba(255,255,255,0.8)', borderRadius: 'var(--radius-sm)', color: 'var(--color-text-secondary)' }}>{b}</span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default LevelPage;
