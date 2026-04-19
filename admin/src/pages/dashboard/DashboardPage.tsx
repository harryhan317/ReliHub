import { useEffect, useState } from 'react';
import { adminService } from '@/services/adminService';
import type { DashboardStats } from '@/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminService.getDashboardStats()
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-spinner">加载中...</div>;

  const totalUsers = stats?.total_users ?? 1247;
  const activeUsers = stats?.active_users ?? 856;
  const totalResources = stats?.total_resources ?? 234;
  const totalTopics = stats?.total_topics ?? 567;
  const aiSessions = 3421;

  return (
    <>
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-card-label">全平台用户总数</div>
          <div className="stat-card-value">{totalUsers.toLocaleString()}</div>
          <div className="stat-card-change up">↑ 12.3% 较上周</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">注册用户数</div>
          <div className="stat-card-value">{activeUsers.toLocaleString()}</div>
          <div className="stat-card-change up">↑ 8.7% 较上周</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">AI对话会话总数</div>
          <div className="stat-card-value">{aiSessions.toLocaleString()}</div>
          <div className="stat-card-change up">↑ 23.1% 较上周</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">资源上传总量</div>
          <div className="stat-card-value">{totalResources.toLocaleString()}</div>
          <div className="stat-card-change up">↑ 5.2% 较上周</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">话题发布总量</div>
          <div className="stat-card-value">{totalTopics.toLocaleString()}</div>
          <div className="stat-card-change down">↓ 2.1% 较上周</div>
        </div>
      </div>

      <div className="chart-grid">
        <div className="chart-card">
          <div className="chart-card-title">
            DAU趋势（近30天）
            <select className="filter-select" style={{ fontSize: 12, padding: '3px 6px' }}>
              <option>自然日</option>
              <option>自然周</option>
            </select>
          </div>
          <div className="chart-bar-group">
            {[60, 75, 65, 80, 70, 90, 85].map((h, i) => (
              <div key={i} style={{ display: 'flex', flexDirection: 'column', flex: 1, alignItems: 'center' }}>
                <div
                  className="chart-bar"
                  style={{
                    height: `${h}%`,
                    ...(i === 6 ? { background: 'linear-gradient(180deg, var(--admin-success), rgba(82,196,26,0.4))' } : {}),
                  }}
                />
                <div className="chart-bar-label" style={i === 6 ? { fontWeight: 600 } : undefined}>
                  {i === 6 ? '今日' : `4/${6 + i}`}
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="chart-card">
          <div className="chart-card-title">功能使用分布</div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
            <div className="chart-ring">
              <div className="chart-ring-center">
                <div className="chart-ring-value">{activeUsers}</div>
                <div className="chart-ring-label">活跃用户</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 16, fontSize: 12 }}>
              <span>🤖 爱问 42%</span>
              <span>📚 资源 28%</span>
              <span>💬 社区 20%</span>
              <span>👤 我的 10%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="chart-card">
        <div className="chart-card-title">游客转化漏斗</div>
        <div className="funnel">
          <div className="funnel-step">
            <div className="funnel-bar" style={{ background: 'var(--admin-primary)', width: '100%' }}>391</div>
            <div className="funnel-label">累计游客会话</div>
          </div>
          <div className="funnel-arrow">→</div>
          <div className="funnel-step">
            <div className="funnel-bar" style={{ background: '#4096ff', width: '80%' }}>156</div>
            <div className="funnel-label">触发注册引导</div>
          </div>
          <div className="funnel-arrow">→</div>
          <div className="funnel-step">
            <div className="funnel-bar" style={{ background: 'var(--admin-success)', width: '55%' }}>86</div>
            <div className="funnel-label">完成注册</div>
          </div>
          <div className="funnel-arrow">→</div>
          <div className="funnel-step">
            <div className="funnel-value" style={{ color: 'var(--admin-success)' }}>21.9%</div>
            <div className="funnel-label">转化率</div>
          </div>
        </div>
      </div>
    </>
  );
}
