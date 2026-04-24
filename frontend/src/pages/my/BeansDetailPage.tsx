import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';
import { useAuthStore } from '../../store/authStore';
import { ledgerService } from '../../services/otherServices';

const BeansDetailPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState(0);
  const [transactions, setTransactions] = useState<Array<{ id: string; type: string; amount: number; balance: number; desc: string; time: string }>>([]);
  const [loading, setLoading] = useState(true);
  const tabs = ['全部', '获取', '消费'];

  useEffect(() => {
    setLoading(true);
    const filterType = activeTab === 0 ? undefined : activeTab === 1 ? 'income' : 'expense';
    ledgerService.getTransactions({ page: 1, page_size: 50 }).then((res) => {
      if (res.data?.items) {
        let items = res.data.items.map((t: any) => ({
          id: t.id,
          type: t.type || (t.amount > 0 ? 'income' : 'expense'),
          amount: t.amount || 0,
          balance: t.balance_after || t.balance || 0,
          desc: t.description || t.desc || '',
          time: t.created_at || '',
        }));
        if (filterType) {
          items = items.filter((t: any) => t.type === filterType || (filterType === 'income' && t.amount > 0) || (filterType === 'expense' && t.amount < 0));
        }
        setTransactions(items);
      }
    }).catch(() => {
      setTransactions([]);
    }).finally(() => setLoading(false));
  }, [activeTab]);

  return (
    <div className="page active">
      <TopBar title="可可豆明细" />
      <div style={{ padding: 'var(--spacing-xl)', textAlign: 'center', background: 'linear-gradient(135deg, var(--color-accent-light), rgba(245,158,11,0.1))' }}>
        <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-secondary)' }}>当前余额</div>
        <div style={{ fontSize: 32, fontWeight: 700, color: 'var(--color-gold)' }}>{user?.cocoa_beans || 0} 🫘</div>
      </div>
      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={setActiveTab} />
      <div className="content-area-no-nav">
        {loading ? (
          <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)', color: 'var(--color-text-muted)' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>⏳</div>
            <div>加载中...</div>
          </div>
        ) : transactions.length > 0 ? (
          transactions.map((t) => (
            <div key={t.id} style={{ padding: 'var(--spacing-md) var(--spacing-lg)', borderBottom: '1px solid var(--color-border-light)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 'var(--font-size-body)', fontWeight: 500 }}>{t.desc}</span>
                <span style={{ fontSize: 'var(--font-size-body)', fontWeight: 700, color: t.amount > 0 ? 'var(--color-success)' : 'var(--color-error)' }}>
                  {t.amount > 0 ? '+' : ''}{t.amount}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
                <span style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)' }}>{t.time ? new Date(t.time).toLocaleString() : ''}</span>
                <span style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)' }}>余额 {t.balance}</span>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">🫘</div>
            <div className="empty-state-text">暂无记录</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BeansDetailPage;
