import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';
import type { AdminUser } from '@/types';

const statusMap: Record<string, { label: string; badge: string }> = {
  PENDING: { label: '待审核', badge: 'badge-warning' },
  APPROVED: { label: '已通过', badge: 'badge-success' },
  REJECTED: { label: '已拒绝', badge: 'badge-error' },
};

export default function UserExpertPage() {
  const [expertUsers, setExpertUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalAction, setModalAction] = useState<{ type: 'approve' | 'reject'; user: AdminUser } | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchExpertUsers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminService.getUsers({ page: 1, page_size: 100 });
      const experts = (res.users || []).filter((u) => u.is_expert);
      setExpertUsers(experts);
    } catch {
      setExpertUsers([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchExpertUsers(); }, [fetchExpertUsers]);

  const filteredApps = expertUsers.filter((u) => {
    if (searchText && !u.nickname.includes(searchText)) return false;
    return true;
  });

  const formatDate = (d: string) => d ? d.slice(0, 10) : '-';

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}

      <div className="toolbar">
        <div className="toolbar-left">
          <div className="search-box">
            <span>🔍</span>
            <input placeholder="搜索用户昵称" value={searchText} onChange={(e) => setSearchText(e.target.value)} />
          </div>
        </div>
      </div>

      {loading ? (
        <div className="loading-spinner">加载中...</div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>UID</th><th>昵称</th><th>等级</th><th>信誉分</th><th>专家状态</th><th>注册时间</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            {filteredApps.map((u) => (
              <tr key={u.id}>
                <td>{u.id.slice(0, 8)}</td>
                <td>{u.nickname}</td>
                <td>{u.rank}</td>
                <td>{u.reputation_points}</td>
                <td><span className="badge badge-success">已认证</span></td>
                <td>{formatDate(u.created_at)}</td>
                <td>
                  <div className="audit-action">
                    <button className="btn btn-sm" onClick={() => { setSelectedUser(u); setDrawerOpen(true); }}>详情</button>
                  </div>
                </td>
              </tr>
            ))}
            {filteredApps.length === 0 && (
              <tr><td colSpan={7} style={{ textAlign: 'center', padding: 32, color: '#999' }}>暂无专家认证数据</td></tr>
            )}
          </tbody>
        </table>
      )}

      <div className={`overlay ${drawerOpen ? 'open' : ''}`} onClick={() => setDrawerOpen(false)} />
      <div className={`detail-drawer ${drawerOpen ? 'open' : ''}`}>
        <div className="detail-drawer-header">
          <div className="detail-drawer-title">认证详情</div>
          <div className="detail-drawer-close" onClick={() => setDrawerOpen(false)}>✕</div>
        </div>
        <div className="detail-drawer-body">
          {selectedUser && (
            <>
              <div className="detail-field"><div className="detail-field-label">UID</div><div className="detail-field-value">{selectedUser.id}</div></div>
              <div className="detail-field"><div className="detail-field-label">昵称</div><div className="detail-field-value">{selectedUser.nickname}</div></div>
              <div className="detail-field"><div className="detail-field-label">等级</div><div className="detail-field-value">{selectedUser.rank}</div></div>
              <div className="detail-field"><div className="detail-field-label">信誉分</div><div className="detail-field-value">{selectedUser.reputation_points}</div></div>
              <div className="detail-field"><div className="detail-field-label">可可豆</div><div className="detail-field-value">{selectedUser.gold_beans}</div></div>
              <div className="detail-field"><div className="detail-field-label">专家认证</div><div className="detail-field-value"><span className="badge badge-success">已认证</span></div></div>
              <div className="detail-field"><div className="detail-field-label">注册时间</div><div className="detail-field-value">{formatDate(selectedUser.created_at)}</div></div>
            </>
          )}
        </div>
      </div>

      {modalOpen && modalAction && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">
              {modalAction.type === 'approve' ? '确认通过专家认证' : '拒绝专家认证'}
            </div>
            <div className="modal-body">
              {modalAction.type === 'approve' ? (
                <p>确定通过「{modalAction.user.nickname}」的专家认证申请吗？</p>
              ) : (
                <div>
                  <p style={{ marginBottom: 12 }}>拒绝「{modalAction.user.nickname}」认证的原因：</p>
                  <textarea
                    className="textarea-input"
                    value={rejectReason}
                    onChange={(e) => setRejectReason(e.target.value)}
                    placeholder="请输入拒绝原因"
                  />
                </div>
              )}
            </div>
            <div className="modal-actions">
              <button className="btn" onClick={() => setModalOpen(false)}>取消</button>
              {modalAction.type === 'approve' ? (
                <button className="btn btn-primary" onClick={() => { showToast('认证已通过', 'success'); setModalOpen(false); }}>确认通过</button>
              ) : (
                <button className="btn btn-danger" onClick={() => { showToast('已拒绝', 'success'); setModalOpen(false); setRejectReason(''); }}>确认拒绝</button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
