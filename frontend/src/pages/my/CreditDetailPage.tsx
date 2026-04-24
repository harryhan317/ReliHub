import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';
import { useAuthStore } from '../../store/authStore';
import { ledgerService } from '../../services/otherServices';

const levelMap: Record<string, { name: string; min: number; max: number }> = {
  '新兵': { name: '新兵', min: 0, max: 99 },
  '菜鸟': { name: '菜鸟', min: 100, max: 299 },
  '入门': { name: '入门', min: 300, max: 699 },
  '熟手': { name: '熟手', min: 700, max: 1499 },
  '老炮': { name: '老炮', min: 1500, max: 2999 },
  '达人': { name: '达人', min: 3000, max: 5999 },
  '专家': { name: '专家', min: 6000, max: 99999 },
};

const CreditDetailPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState(0);
  const [records, setRecords] = useState<Array<{ id: string; type: string; amount: number; score: number; desc: string; time: string }>>([]);
  const [loading, setLoading] = useState(true);
  const tabs = ['全部', '获取', '扣减'];

  const currentLevel = user?.level || '新兵';
  const levelInfo = levelMap[currentLevel] || levelMap['新兵'];
  const creditScore = user?.credit_score || 0;
  const progress = Math.min(100, ((creditScore - levelInfo.min) / (levelInfo.max - levelInfo.min)) * 100);
  const nextLevel = Object.entries(levelMap).find(([_, v]) => v.min > creditScore);

  useEffect(() => {
    setLoading(true);
    ledgerService.getTransactions({ page: 1, page_size: 50 }).then((res) => {
      if (res.data?.items) {
        let items = res.data.items
          .filter((t: any) => t.type === 'credit' || t.category === 'credit')
          .map((t: any) => ({
            id: t.id,
            type: t.amount > 0 ? 'income' : 'expense',
            amount: t.amount || 0,
            score: t.balance_after || 0,
            desc: t.description || t.desc || '',
            time: t.created_at || '',
          }));
        if (activeTab === 1) items = items.filter((t) => t.amount > 0);
        if (activeTab === 2) items = items.filter((t) => t.amount < 0);
        setRecords(items);
      }
    }).catch(() => {
      setRecords([]);
    }).finally(() => setLoading(false));
  }, [activeTab]);

  return (
    <div className="page active">
      <TopBar title="信誉分明细" />
      <div style={{ padding: 'var(--spacing-xl)', textAlign: 'center', background: 'linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1))' }}>
        <div style={{ fontSize: 32, fontWeight: 700, color: 'var(--color-accent)' }}>{creditScore} 分</div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--spacing-sm)', marginTop: 'var(--spacing-sm)' }}>
          <span style={{ fontSize: 'var(--font-size-body)', fontWeight: 600, color: 'var(--color-accent)' }}>{currentLevel}</span>
          {nextLevel && (
            <span style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)' }}>
              → {nextLevel[0]}（还需 {nextLevel[1].min - creditScore} 分）
            </span>
          )}
        </div>
        <div style={{ margin: 'var(--spacing-md) auto 0', maxWidth: 200, height: 6, background: 'var(--color-bg-secondary)', borderRadius: 3, overflow: 'hidden' }}>
          <div style={{ width: `${progress}%`, height: '100%', background: 'var(--color-accent)', borderRadius: 3, transition: 'width 0.3s' }}></div>
        </div>
      </div>
      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={setActiveTab} />
      <div className="content-area-no-nav">
        {loading ? (
          <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)', color: 'var(--color-text-muted)' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>⏳</div>
            <div>加载中...</div>
          </div>
        ) : records.length > 0 ? (
          records.map((r) => (
            <div key={r.id} style={{ padding: 'var(--spacing-md) var(--spacing-lg)', borderBottom: '1px solid var(--color-border-light)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 'var(--font-size-body)', fontWeight: 500 }}>{r.desc}</span>
                <span style={{ fontSize: 'var(--font-size-body)', fontWeight: 700, color: r.amount > 0 ? 'var(--color-success)' : 'var(--color-error)' }}>
                  {r.amount > 0 ? '+' : ''}{r.amount}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
                <span style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)' }}>{r.time ? new Date(r.time).toLocaleString() : ''}</span>
                <span style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)' }}>当前 {r.score} 分</span>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">⭐</div>
            <div className="empty-state-text">暂无记录</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CreditDetailPage;
