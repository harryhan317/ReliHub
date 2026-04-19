import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';
import type { AdminUser } from '@/types';

const statusMap: Record<string, { label: string; badge: string }> = {
  ACTIVE: { label: '正常', badge: 'badge-success' },
  FROZEN: { label: '冻结', badge: 'badge-warning' },
  BANNED: { label: '永久封禁', badge: 'badge-error' },
  TEMP_BANNED: { label: '临时封禁', badge: 'badge-error' },
  LOCKED: { label: '安全锁定', badge: 'badge-error' },
  DISABLED: { label: '已警告', badge: 'badge-warning' },
  HIBERNATED: { label: '休眠', badge: 'badge-info' },
};

const rankMap: Record<string, { label: string; badge: string }> = {
  '新兵': { label: '新兵', badge: 'badge-info' },
  '菜鸟': { label: '菜鸟', badge: 'badge-info' },
  '入门': { label: '入门', badge: 'badge-primary' },
  '熟手': { label: '熟手', badge: 'badge-primary' },
  '老炮': { label: '老炮', badge: 'badge-success' },
  '达人': { label: '达人', badge: 'badge-warning' },
  '专家': { label: '专家', badge: 'badge-error' },
};

const DETAIL_TABS = ['个人信息', '贡献记录', '账户快照', '信誉分明细', '操作历史'];

export default function UserListPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [rankFilter, setRankFilter] = useState('');
  const [searchText, setSearchText] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [detailTab, setDetailTab] = useState(0);
  const [penaltyModal, setPenaltyModal] = useState<'warn' | 'deduct_credit' | 'restrict' | 'temp_ban' | 'perm_ban' | null>(null);
  const [penaltyReason, setPenaltyReason] = useState('');
  const [penaltyValue, setPenaltyValue] = useState('');
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminService.getUsers({
        status: statusFilter || undefined,
        search: searchText || undefined,
        page,
        page_size: 20,
      });
      setUsers(res.users || []);
      setTotal(res.total);
    } catch {
      setUsers([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, searchText, page]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const totalPages = Math.ceil(total / 20);

  const maskPhone = (phone: string | null) => {
    if (!phone) return '-';
    if (phone.length >= 7) return phone.slice(0, 3) + '****' + phone.slice(-4);
    return phone;
  };

  const formatDate = (d: string) => d ? d.slice(0, 10) : '-';

  const handlePenalty = () => {
    if (!penaltyReason.trim()) {
      showToast('请填写操作原因', 'error');
      return;
    }
    showToast('操作已执行（对接后端API后生效）', 'success');
    setPenaltyModal(null);
    setPenaltyReason('');
    setPenaltyValue('');
  };

  const handleUnlock = () => {
    showToast('账号已解锁（对接后端API后生效）', 'success');
  };

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}

      <div className="toolbar">
        <div className="toolbar-left" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <select className="filter-select" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
            <option value="">全部状态</option>
            <option value="ACTIVE">正常</option>
            <option value="FROZEN">冻结 ⚠️</option>
            <option value="TEMP_BANNED">临时封禁</option>
            <option value="BANNED">永久封禁</option>
            <option value="LOCKED">安全锁定 🔒</option>
            <option value="HIBERNATED">休眠</option>
          </select>
          <select className="filter-select" value={rankFilter} onChange={(e) => { setRankFilter(e.target.value); setPage(1); }}>
            <option value="">全部等级</option>
            {Object.keys(rankMap).map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
          <div className="search-box">
            <span>🔍</span>
            <input placeholder="搜索用户昵称/手机号" value={searchText} onChange={(e) => { setSearchText(e.target.value); setPage(1); }} />
          </div>
        </div>
        <div className="toolbar-right">
          <button className="btn">📥 导出</button>
        </div>
      </div>

      {loading ? (
        <div className="loading-spinner">加载中...</div>
      ) : (
        <>
          <table className="data-table">
            <thead>
              <tr>
                <th>UID</th><th>昵称</th><th>手机号</th><th>等级</th><th>信誉分</th><th>可可豆</th><th>状态</th><th>注册时间</th><th>最近登录</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.id.slice(0, 8)}</td>
                  <td>{u.nickname}</td>
                  <td>{maskPhone(u.phone)}</td>
                  <td><span className={`badge ${rankMap[u.rank]?.badge || 'badge-info'}`}>{rankMap[u.rank]?.label || u.rank}</span></td>
                  <td>{u.reputation_points}</td>
                  <td>{u.gold_beans}</td>
                  <td><span className={`badge ${statusMap[u.status]?.badge || 'badge-info'}`}>{statusMap[u.status]?.label || u.status}</span></td>
                  <td>{formatDate(u.created_at)}</td>
                  <td>-</td>
                  <td>
                    <div className="audit-action">
                      <button className="btn btn-sm" onClick={() => { setSelectedUser(u); setDrawerOpen(true); setDetailTab(0); }}>详情</button>
                    </div>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr><td colSpan={10} style={{ textAlign: 'center', padding: 32, color: '#999' }}>暂无数据</td></tr>
              )}
            </tbody>
          </table>

          {totalPages > 1 && (
            <div className="pagination">
              <div className={`pagination-btn ${page <= 1 ? 'disabled' : ''}`} onClick={() => page > 1 && setPage(page - 1)}>‹</div>
              {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                const p = i + 1;
                return <div key={p} className={`pagination-btn ${p === page ? 'active' : ''}`} onClick={() => setPage(p)}>{p}</div>;
              })}
              <div className={`pagination-btn ${page >= totalPages ? 'disabled' : ''}`} onClick={() => page < totalPages && setPage(page + 1)}>›</div>
            </div>
          )}
        </>
      )}

      <div className={`overlay ${drawerOpen ? 'open' : ''}`} onClick={() => setDrawerOpen(false)} />
      <div className={`detail-drawer ${drawerOpen ? 'open' : ''}`} style={{ width: 560 }}>
        <div className="detail-drawer-header">
          <div className="detail-drawer-title">用户详情</div>
          <div className="detail-drawer-close" onClick={() => setDrawerOpen(false)}>✕</div>
        </div>
        <div className="detail-drawer-body">
          {selectedUser && (
            <>
              <div style={{ display: 'flex', gap: 0, marginBottom: 16, borderBottom: '1px solid #f0f0f0' }}>
                {DETAIL_TABS.map((tab, idx) => (
                  <button
                    key={tab}
                    onClick={() => setDetailTab(idx)}
                    style={{
                      padding: '8px 12px',
                      fontSize: 13,
                      border: 'none',
                      background: 'none',
                      cursor: 'pointer',
                      borderBottom: detailTab === idx ? '2px solid #1890ff' : '2px solid transparent',
                      color: detailTab === idx ? '#1890ff' : '#666',
                      fontWeight: detailTab === idx ? 600 : 400,
                    }}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {detailTab === 0 && (
                <>
                  <div className="detail-field"><div className="detail-field-label">UID</div><div className="detail-field-value">{selectedUser.id}</div></div>
                  <div className="detail-field"><div className="detail-field-label">昵称</div><div className="detail-field-value">{selectedUser.nickname}</div></div>
                  <div className="detail-field"><div className="detail-field-label">手机号</div><div className="detail-field-value">{maskPhone(selectedUser.phone)}</div></div>
                  <div className="detail-field"><div className="detail-field-label">等级</div><div className="detail-field-value"><span className={`badge ${rankMap[selectedUser.rank]?.badge || 'badge-info'}`}>{rankMap[selectedUser.rank]?.label || selectedUser.rank}</span></div></div>
                  <div className="detail-field"><div className="detail-field-label">信誉分</div><div className="detail-field-value">{selectedUser.reputation_points}</div></div>
                  <div className="detail-field"><div className="detail-field-label">可可豆余额</div><div className="detail-field-value">{selectedUser.gold_beans}</div></div>
                  <div className="detail-field"><div className="detail-field-label">状态</div><div className="detail-field-value"><span className={`badge ${statusMap[selectedUser.status]?.badge || 'badge-info'}`}>{statusMap[selectedUser.status]?.label || selectedUser.status}</span></div></div>
                  <div className="detail-field"><div className="detail-field-label">注册时间</div><div className="detail-field-value">{formatDate(selectedUser.created_at)}</div></div>
                </>
              )}

              {detailTab === 1 && (
                <div style={{ color: '#999', textAlign: 'center', padding: 32 }}>
                  上传资源列表 / 发起话题列表 / 参与回复列表（对接后端API后展示）
                </div>
              )}

              {detailTab === 2 && (
                <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                  <div style={{ flex: '1 1 45%', padding: 12, background: '#f6ffed', borderRadius: 6 }}>
                    <div style={{ fontSize: 12, color: '#999' }}>可可豆余额</div>
                    <div style={{ fontSize: 20, fontWeight: 600 }}>{selectedUser.gold_beans}</div>
                  </div>
                  <div style={{ flex: '1 1 45%', padding: 12, background: '#f0f5ff', borderRadius: 6 }}>
                    <div style={{ fontSize: 12, color: '#999' }}>累计获取</div>
                    <div style={{ fontSize: 20, fontWeight: 600, color: '#1890ff' }}>-</div>
                  </div>
                  <div style={{ flex: '1 1 45%', padding: 12, background: '#fff1f0', borderRadius: 6 }}>
                    <div style={{ fontSize: 12, color: '#999' }}>累计消耗</div>
                    <div style={{ fontSize: 20, fontWeight: 600, color: '#ff4d4f' }}>-</div>
                  </div>
                  <div style={{ flex: '1 1 45%', padding: 12, background: '#fff7e6', borderRadius: 6 }}>
                    <div style={{ fontSize: 12, color: '#999' }}>累计销毁</div>
                    <div style={{ fontSize: 20, fontWeight: 600, color: '#fa8c16' }}>-</div>
                  </div>
                </div>
              )}

              {detailTab === 3 && (
                <div style={{ color: '#999', textAlign: 'center', padding: 32 }}>
                  信誉分历史变动流水（时间/变动原因/变动值/变动后余额）- 对接后端API后展示
                </div>
              )}

              {detailTab === 4 && (
                <div style={{ color: '#999', textAlign: 'center', padding: 32 }}>
                  该用户被管理员执行过的所有操作记录（处置/解锁/等级变更等）- 对接后端API后展示
                </div>
              )}

              <div style={{ marginTop: 24, borderTop: '1px solid #f0f0f0', paddingTop: 16 }}>
                <div style={{ fontWeight: 600, marginBottom: 8, fontSize: 13 }}>违规处置（§7.2）</div>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  <button className="btn btn-sm" onClick={() => setPenaltyModal('warn')}>⚠️ 警告通知</button>
                  <button className="btn btn-sm" onClick={() => setPenaltyModal('deduct_credit')}>📉 扣减信誉分</button>
                  <button className="btn btn-sm" onClick={() => setPenaltyModal('restrict')}>🚫 限制功能</button>
                  <button className="btn btn-sm" onClick={() => setPenaltyModal('temp_ban')}>⏸️ 临时封禁</button>
                  <button className="btn btn-sm" style={{ color: '#ff4d4f' }} onClick={() => setPenaltyModal('perm_ban')}>🚫 永久封禁</button>
                  {selectedUser.status === 'LOCKED' && (
                    <button className="btn btn-primary btn-sm" onClick={handleUnlock}>🔓 解锁账号</button>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {penaltyModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1001, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', borderRadius: 12, padding: 24, width: 420 }}>
            <h3 style={{ margin: '0 0 16px' }}>
              {penaltyModal === 'warn' && '发送警告通知'}
              {penaltyModal === 'deduct_credit' && '扣减信誉分'}
              {penaltyModal === 'restrict' && '限制功能权限'}
              {penaltyModal === 'temp_ban' && '临时封禁'}
              {penaltyModal === 'perm_ban' && '永久封禁'}
            </h3>

            {penaltyModal === 'deduct_credit' && (
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 13, color: '#666' }}>扣减分值（1~200分）</label>
                <input
                  className="config-input"
                  type="number"
                  min={1}
                  max={200}
                  value={penaltyValue}
                  onChange={(e) => setPenaltyValue(e.target.value)}
                  style={{ width: '100%', marginTop: 4 }}
                />
              </div>
            )}

            {penaltyModal === 'temp_ban' && (
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 13, color: '#666' }}>解封日期</label>
                <input
                  className="config-input"
                  type="date"
                  value={penaltyValue}
                  onChange={(e) => setPenaltyValue(e.target.value)}
                  style={{ width: '100%', marginTop: 4 }}
                />
              </div>
            )}

            {penaltyModal === 'restrict' && (
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 13, color: '#666' }}>限制功能</label>
                <div style={{ marginTop: 4, display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {['下载', '发起话题', '发起悬赏', 'AI对话'].map((f) => (
                    <label key={f} style={{ fontSize: 13 }}><input type="checkbox" style={{ marginRight: 6 }} />{f}</label>
                  ))}
                </div>
              </div>
            )}

            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 13, color: '#666' }}>操作原因（必填）</label>
              <textarea
                value={penaltyReason}
                onChange={(e) => setPenaltyReason(e.target.value)}
                style={{ width: '100%', marginTop: 4, padding: 8, border: '1px solid #d9d9d9', borderRadius: 6, minHeight: 80, fontSize: 13 }}
                placeholder="请输入操作原因..."
              />
            </div>

            {penaltyModal === 'perm_ban' && (
              <div style={{ padding: '8px 12px', background: '#fff1f0', borderRadius: 6, fontSize: 13, color: '#ff4d4f', marginBottom: 12 }}>
                ⚠️ 永久封禁为不可逆操作，仅超级管理员可执行。需二次短信验证确认。
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button className="btn btn-sm" onClick={() => { setPenaltyModal(null); setPenaltyReason(''); setPenaltyValue(''); }}>取消</button>
              <button className="btn btn-primary btn-sm" onClick={handlePenalty}>确认执行</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
