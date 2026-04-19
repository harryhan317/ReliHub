import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';
import type { AdminUser } from '@/types';

const statusMap: Record<string, { label: string; badge: string }> = {
  ACTIVE: { label: '正常', badge: 'badge-success' },
  DISABLED: { label: '已警告', badge: 'badge-warning' },
  LOCKED: { label: '已封禁', badge: 'badge-error' },
  HIBERNATED: { label: '休眠', badge: 'badge-info' },
};

const rankMap: Record<string, { label: string; badge: string }> = {
  '新兵': { label: '新兵', badge: 'badge-info' },
  '菜鸟': { label: '菜鸟', badge: 'badge-info' },
  '入门': { label: '入门', badge: 'badge-success' },
  '熟手': { label: '熟手', badge: 'badge-success' },
  '老炮': { label: '老炮', badge: 'badge-warning' },
  '达人': { label: '达人', badge: 'badge-warning' },
  '专家': { label: '专家', badge: 'badge-error' },
};

export default function UserListPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [searchText, setSearchText] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);

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

  const totalPages = Math.ceil(total / 20);

  const maskPhone = (phone: string | null) => {
    if (!phone) return '-';
    if (phone.length >= 7) return phone.slice(0, 3) + '****' + phone.slice(-4);
    return phone;
  };

  const formatDate = (d: string) => d ? d.slice(0, 10) : '-';

  return (
    <>
      <div className="toolbar">
        <div className="toolbar-left">
          <select className="filter-select" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
            <option value="">全部状态</option>
            <option value="ACTIVE">正常</option>
            <option value="DISABLED">已警告</option>
            <option value="LOCKED">已封禁</option>
            <option value="HIBERNATED">休眠</option>
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
                <th>UID</th><th>昵称</th><th>手机号</th><th>等级</th><th>信誉分</th><th>可可豆</th><th>状态</th><th>注册时间</th><th>操作</th>
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
                  <td>
                    <div className="audit-action">
                      <button className="btn btn-sm" onClick={() => { setSelectedUser(u); setDrawerOpen(true); }}>详情</button>
                    </div>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr><td colSpan={9} style={{ textAlign: 'center', padding: 32, color: '#999' }}>暂无数据</td></tr>
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
      <div className={`detail-drawer ${drawerOpen ? 'open' : ''}`}>
        <div className="detail-drawer-header">
          <div className="detail-drawer-title">用户详情</div>
          <div className="detail-drawer-close" onClick={() => setDrawerOpen(false)}>✕</div>
        </div>
        <div className="detail-drawer-body">
          {selectedUser && (
            <>
              <div className="detail-field"><div className="detail-field-label">UID</div><div className="detail-field-value">{selectedUser.id}</div></div>
              <div className="detail-field"><div className="detail-field-label">昵称</div><div className="detail-field-value">{selectedUser.nickname}</div></div>
              <div className="detail-field"><div className="detail-field-label">手机号</div><div className="detail-field-value">{maskPhone(selectedUser.phone)}</div></div>
              <div className="detail-field"><div className="detail-field-label">等级</div><div className="detail-field-value"><span className={`badge ${rankMap[selectedUser.rank]?.badge || 'badge-info'}`}>{rankMap[selectedUser.rank]?.label || selectedUser.rank}</span></div></div>
              <div className="detail-field"><div className="detail-field-label">信誉分</div><div className="detail-field-value">{selectedUser.reputation_points}</div></div>
              <div className="detail-field"><div className="detail-field-label">可可豆</div><div className="detail-field-value">{selectedUser.gold_beans}</div></div>
              <div className="detail-field"><div className="detail-field-label">状态</div><div className="detail-field-value"><span className={`badge ${statusMap[selectedUser.status]?.badge || 'badge-info'}`}>{statusMap[selectedUser.status]?.label || selectedUser.status}</span></div></div>
              <div className="detail-field"><div className="detail-field-label">注册时间</div><div className="detail-field-value">{formatDate(selectedUser.created_at)}</div></div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
