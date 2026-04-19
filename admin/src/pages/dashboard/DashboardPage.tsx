import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';
import type { DashboardStats } from '@/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showBroadcast, setShowBroadcast] = useState(false);
  const [broadcastMsg, setBroadcastMsg] = useState('');
  const [broadcastReason, setBroadcastReason] = useState('');
  const [broadcastSending, setBroadcastSending] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    adminService.getDashboardStats()
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleBroadcast = useCallback(async () => {
    if (!broadcastMsg.trim()) {
      showToast('请输入广播内容', 'error');
      return;
    }
    if (!broadcastReason.trim()) {
      showToast('请填写操作原因', 'error');
      return;
    }
    setBroadcastSending(true);
    try {
      showToast('系统通知已广播（对接后端API后生效）', 'success');
      setShowBroadcast(false);
      setBroadcastMsg('');
      setBroadcastReason('');
    } finally {
      setBroadcastSending(false);
    }
  }, [broadcastMsg, broadcastReason]);

  if (loading) return <div className="loading-spinner">加载中...</div>;

  const totalUsers = stats?.total_users ?? 1247;
  const activeUsers = stats?.active_users ?? 856;
  const totalResources = stats?.total_resources ?? 234;
  const totalTopics = stats?.total_topics ?? 567;

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3 style={{ margin: 0 }}>系统看板</h3>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-sm" onClick={() => setShowBroadcast(true)}>📢 系统广播</button>
          <button className="btn btn-sm" onClick={() => showToast('数据导出功能（对接后端API后实现）', 'success')}>📥 导出数据</button>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-card-label">全平台用户总数</div>
          <div className="stat-card-value">{totalUsers.toLocaleString()}</div>
          <div className="stat-card-change up">↑ 12.3% 较上周</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">注册用户数</div>
          <div className="stat-card-value">{(totalUsers - 391).toLocaleString()}</div>
          <div className="stat-card-change up">↑ 15.2% 较上周</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">DAU（日活跃用户）</div>
          <div className="stat-card-value">{activeUsers.toLocaleString()}</div>
          <div className="stat-card-change up">↑ 8.7% 较上周</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">MAU（月活跃用户）</div>
          <div className="stat-card-value">1,024</div>
          <div className="stat-card-change up">↑ 5.3% 较上月</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">AI对话会话总数</div>
          <div className="stat-card-value">3,421</div>
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
        <div className="stat-card">
          <div className="stat-card-label">待审核资源</div>
          <div className="stat-card-value" style={{ color: '#fa8c16' }}>18</div>
          <div className="stat-card-change">SLA倒计时进行中</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">待审核社区内容</div>
          <div className="stat-card-value" style={{ color: '#fa8c16' }}>7</div>
          <div className="stat-card-change">含AI可疑内容</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">今日新增注册</div>
          <div className="stat-card-value">42</div>
          <div className="stat-card-change up">↑ 15.2% 较昨日</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">AI Token日消耗</div>
          <div className="stat-card-value">128K</div>
          <div className="stat-card-change">估算费用 ¥12.8</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">社区发帖量（今日）</div>
          <div className="stat-card-value">23</div>
          <div className="stat-card-change up">↑ 10.5% 较昨日</div>
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

      <div className="chart-grid">
        <div className="chart-card">
          <div className="chart-card-title">留存率统计</div>
          <div style={{ display: 'flex', gap: 24, justifyContent: 'center', padding: '16px 0' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: '#52c41a' }}>45.2%</div>
              <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>次日留存</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: '#1890ff' }}>28.7%</div>
              <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>7日留存</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: '#722ed1' }}>15.3%</div>
              <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>30日留存</div>
            </div>
          </div>
          <div style={{ color: '#999', fontSize: 12, textAlign: 'center' }}>
            支持按注册渠道维度拆分查看留存差异
          </div>
        </div>
        <div className="chart-card">
          <div className="chart-card-title">可可豆与Token流转</div>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', padding: '12px 0' }}>
            <div style={{ flex: '1 1 45%', padding: '8px 12px', background: '#f6ffed', borderRadius: 6 }}>
              <div style={{ fontSize: 12, color: '#999' }}>今日发放</div>
              <div style={{ fontSize: 20, fontWeight: 600, color: '#52c41a' }}>+2,450</div>
            </div>
            <div style={{ flex: '1 1 45%', padding: '8px 12px', background: '#fff1f0', borderRadius: 6 }}>
              <div style={{ fontSize: 12, color: '#999' }}>今日消耗</div>
              <div style={{ fontSize: 20, fontWeight: 600, color: '#ff4d4f' }}>-1,820</div>
            </div>
            <div style={{ flex: '1 1 45%', padding: '8px 12px', background: '#f0f5ff', borderRadius: 6 }}>
              <div style={{ fontSize: 12, color: '#999' }}>今日销毁</div>
              <div style={{ fontSize: 20, fontWeight: 600, color: '#1890ff' }}>-546</div>
            </div>
            <div style={{ flex: '1 1 45%', padding: '8px 12px', background: '#fff7e6', borderRadius: 6 }}>
              <div style={{ fontSize: 12, color: '#999' }}>今日净增</div>
              <div style={{ fontSize: 20, fontWeight: 600, color: '#fa8c16' }}>+84</div>
            </div>
          </div>
          <div style={{ color: '#999', fontSize: 12, textAlign: 'center' }}>
            Token日消耗128K | 估算费用¥12.8 | 按模型版本拆分
          </div>
        </div>
      </div>

      <div className="chart-card">
        <div className="chart-card-title">游客转化漏斗（§4.1）</div>
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
        <div style={{ color: '#999', fontSize: 12, marginTop: 8, textAlign: 'center' }}>
          转化率 = 当日新增注册用户数 ÷ 当日有会话的游客数 × 100% | 支持按渠道维度（UTM参数）二次筛选
        </div>
      </div>

      <div className="chart-grid" style={{ marginTop: 16 }}>
        <div className="chart-card">
          <div className="chart-card-title">AI对话频次（§4.2）</div>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', padding: '12px 0' }}>
            <div style={{ flex: '1 1 45%', padding: '8px 12px', background: '#f0f5ff', borderRadius: 6 }}>
              <div style={{ fontSize: 12, color: '#999' }}>平均每用户每日会话数</div>
              <div style={{ fontSize: 20, fontWeight: 600 }}>4.2</div>
            </div>
            <div style={{ flex: '1 1 45%', padding: '8px 12px', background: '#f0f5ff', borderRadius: 6 }}>
              <div style={{ fontSize: 12, color: '#999' }}>单会话平均轮次</div>
              <div style={{ fontSize: 20, fontWeight: 600 }}>6.8</div>
            </div>
          </div>
        </div>
        <div className="chart-card">
          <div className="chart-card-title">资源下载量（§4.2）</div>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', padding: '12px 0' }}>
            <div style={{ flex: '1 1 45%', padding: '8px 12px', background: '#f6ffed', borderRadius: 6 }}>
              <div style={{ fontSize: 12, color: '#999' }}>日均下载次数</div>
              <div style={{ fontSize: 20, fontWeight: 600 }}>156</div>
            </div>
            <div style={{ flex: '1 1 45%', padding: '8px 12px', background: '#f6ffed', borderRadius: 6 }}>
              <div style={{ fontSize: 12, color: '#999' }}>下载分布</div>
              <div style={{ fontSize: 13, lineHeight: 1.8 }}>
                0~10豆: 45% | 10~50豆: 30% | 50~100豆: 18% | 100+豆: 7%
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="chart-grid" style={{ marginTop: 16 }}>
        <div className="chart-card">
          <div className="chart-card-title">社区发帖量（§4.2）</div>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', padding: '12px 0' }}>
            <div style={{ flex: '1 1 45%', padding: '8px 12px', background: '#f0f5ff', borderRadius: 6 }}>
              <div style={{ fontSize: 12, color: '#999' }}>日均话题发布数</div>
              <div style={{ fontSize: 20, fontWeight: 600 }}>23</div>
            </div>
            <div style={{ flex: '1 1 45%', padding: '8px 12px', background: '#f0f5ff', borderRadius: 6 }}>
              <div style={{ fontSize: 12, color: '#999' }}>日均回复数</div>
              <div style={{ fontSize: 20, fontWeight: 600 }}>87</div>
            </div>
          </div>
        </div>
        <div className="chart-card">
          <div className="chart-card-title">数据筛选与导出（§4.4）</div>
          <div style={{ padding: '12px 0' }}>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
              <select className="config-input" style={{ width: 120 }}>
                <option value="">业务模块</option>
                <option>AI对话</option>
                <option>资源</option>
                <option>社区</option>
                <option>用户</option>
              </select>
              <input className="config-input" type="date" style={{ width: 140 }} />
              <span style={{ lineHeight: '32px' }}>至</span>
              <input className="config-input" type="date" style={{ width: 140 }} />
              <button className="btn btn-primary btn-sm">筛选</button>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-sm" onClick={() => showToast('CSV导出（对接后端API后实现）', 'success')}>📥 导出CSV</button>
              <button className="btn btn-sm" onClick={() => showToast('Excel导出（对接后端API后实现）', 'success')}>📥 导出Excel</button>
            </div>
            <div style={{ color: '#999', fontSize: 12, marginTop: 8 }}>
              导出文件包含数据源、时间范围、筛选条件、导出时间等元信息注脚
            </div>
          </div>
        </div>
      </div>

      {showBroadcast && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1001, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', borderRadius: 12, padding: 24, width: 520 }}>
            <h3 style={{ margin: '0 0 16px' }}>📢 系统通知广播（§4.5 M5-F011）</h3>
            <div style={{ padding: '8px 12px', background: '#fff7e6', borderRadius: 6, fontSize: 13, color: '#ad6800', marginBottom: 12 }}>
              ⚠️ 全量广播每自然日上限1次，每次需填写操作原因并记录审计日志。广播消息不受用户免打扰时段约束。
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>广播内容</label>
              <textarea
                value={broadcastMsg}
                onChange={(e) => setBroadcastMsg(e.target.value)}
                style={{ width: '100%', marginTop: 4, padding: 8, border: '1px solid #d9d9d9', borderRadius: 6, minHeight: 100, fontSize: 13 }}
                placeholder="输入系统通知广播内容..."
              />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>操作原因（必填）</label>
              <input
                className="config-input"
                type="text"
                value={broadcastReason}
                onChange={(e) => setBroadcastReason(e.target.value)}
                style={{ width: '100%', marginTop: 4 }}
                placeholder="请输入本次广播的操作原因"
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button className="btn btn-sm" onClick={() => { setShowBroadcast(false); setBroadcastMsg(''); setBroadcastReason(''); }}>取消</button>
              <button className="btn btn-primary btn-sm" onClick={handleBroadcast} disabled={broadcastSending}>
                {broadcastSending ? '发送中...' : '确认广播'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
