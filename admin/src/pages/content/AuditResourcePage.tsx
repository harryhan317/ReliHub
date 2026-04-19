import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';
import type { ResourceItem } from '@/types';

const statusMap: Record<string, { label: string; badge: string }> = {
  PENDING_REVIEW: { label: '待审核', badge: 'badge-warning' },
  APPROVED: { label: '已通过', badge: 'badge-success' },
  REJECTED: { label: '已拒绝', badge: 'badge-error' },
  BLOCKED: { label: '已封禁', badge: 'badge-error' },
  APPEALING: { label: '申诉中', badge: 'badge-info' },
};

const categoryMap: Record<number, string> = {
  1: '标准规范',
  2: '社区话题',
  3: '应用笔记',
  4: '培训资料',
  5: '案例分享',
  6: '器件手册',
};

export default function AuditResourcePage() {
  const [resources, setResources] = useState<ResourceItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [searchText, setSearchText] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedResource, setSelectedResource] = useState<ResourceItem | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalAction, setModalAction] = useState<{ type: 'approve' | 'reject'; resource: ResourceItem } | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchResources = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminService.getResources({
        status: statusFilter || undefined,
        page,
        page_size: 20,
      });
      setResources(res.resources || []);
      setTotal(res.total);
    } catch {
      setResources([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, page]);

  useEffect(() => { fetchResources(); }, [fetchResources]);

  const handleApprove = useCallback(async (resourceId: string) => {
    try {
      await adminService.approveResource(resourceId);
      showToast('审核通过', 'success');
      fetchResources();
    } catch {
      showToast('操作失败', 'error');
    }
    setModalOpen(false);
    setModalAction(null);
  }, [fetchResources]);

  const handleReject = useCallback(async (resourceId: string, reason: string) => {
    try {
      await adminService.rejectResource(resourceId, reason);
      showToast('已拒绝', 'success');
      fetchResources();
    } catch {
      showToast('操作失败', 'error');
    }
    setModalOpen(false);
    setModalAction(null);
    setRejectReason('');
  }, [fetchResources]);

  const filteredResources = resources.filter((r) => {
    if (searchText && !r.title.includes(searchText)) return false;
    return true;
  });

  const formatDate = (d: string) => d ? d.slice(0, 16).replace('T', ' ') : '-';
  const totalPages = Math.ceil(total / 20);

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}

      <div className="toolbar">
        <div className="toolbar-left">
          <select className="filter-select" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
            <option value="">全部状态</option>
            <option value="PENDING_REVIEW">待审核</option>
            <option value="APPROVED">已通过</option>
            <option value="REJECTED">已拒绝</option>
            <option value="APPEALING">申诉中</option>
          </select>
          <div className="search-box">
            <span>🔍</span>
            <input placeholder="搜索资源标题/上传者" value={searchText} onChange={(e) => setSearchText(e.target.value)} />
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
                <th>ID</th><th>资源标题</th><th>分类</th><th>定价</th><th>状态</th><th>提交时间</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredResources.map((r) => (
                <tr key={r.id}>
                  <td>{r.id.slice(0, 8)}</td>
                  <td>{r.title}</td>
                  <td>{categoryMap[r.category_id] || r.category_id}</td>
                  <td>{r.price > 0 ? `${r.price} 🫘` : '免费'}</td>
                  <td><span className={`badge ${statusMap[r.status]?.badge || 'badge-default'}`}>{statusMap[r.status]?.label || r.status}</span></td>
                  <td>{formatDate(r.created_at)}</td>
                  <td>
                    <div className="audit-action">
                      {r.status === 'PENDING_REVIEW' && (
                        <>
                          <button className="btn btn-primary btn-sm" onClick={() => { setModalAction({ type: 'approve', resource: r }); setModalOpen(true); }}>通过</button>
                          <button className="btn btn-danger btn-sm" onClick={() => { setModalAction({ type: 'reject', resource: r }); setModalOpen(true); }}>拒绝</button>
                        </>
                      )}
                      {r.status === 'APPEALING' && (
                        <button className="btn btn-primary btn-sm">处理申诉</button>
                      )}
                      <button className="btn btn-sm" onClick={() => { setSelectedResource(r); setDrawerOpen(true); }}>详情</button>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredResources.length === 0 && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: 32, color: '#999' }}>暂无数据</td></tr>
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
          <div className="detail-drawer-title">详情查看</div>
          <div className="detail-drawer-close" onClick={() => setDrawerOpen(false)}>✕</div>
        </div>
        <div className="detail-drawer-body">
          {selectedResource && (
            <>
              <div className="detail-field"><div className="detail-field-label">ID</div><div className="detail-field-value">{selectedResource.id}</div></div>
              <div className="detail-field"><div className="detail-field-label">标题</div><div className="detail-field-value">{selectedResource.title}</div></div>
              <div className="detail-field"><div className="detail-field-label">分类</div><div className="detail-field-value">{categoryMap[selectedResource.category_id] || selectedResource.category_id}</div></div>
              <div className="detail-field"><div className="detail-field-label">定价</div><div className="detail-field-value">{selectedResource.price > 0 ? `${selectedResource.price} 🫘` : '免费'}</div></div>
              <div className="detail-field"><div className="detail-field-label">状态</div><div className="detail-field-value"><span className={`badge ${statusMap[selectedResource.status]?.badge}`}>{statusMap[selectedResource.status]?.label || selectedResource.status}</span></div></div>
              <div className="detail-field"><div className="detail-field-label">提交时间</div><div className="detail-field-value">{formatDate(selectedResource.created_at)}</div></div>
              <div className="detail-field"><div className="detail-field-label">浏览/下载</div><div className="detail-field-value">{selectedResource.view_count} / {selectedResource.download_count}</div></div>
              <div className="detail-field"><div className="detail-field-label">简介</div><div className="detail-field-value">{selectedResource.description || '-'}</div></div>
              {selectedResource.status === 'PENDING_REVIEW' && (
                <div style={{ marginTop: 20, display: 'flex', gap: 8 }}>
                  <button className="btn btn-primary" onClick={() => handleApprove(selectedResource.id)}>通过审核</button>
                  <button className="btn btn-danger" onClick={() => { setModalAction({ type: 'reject', resource: selectedResource }); setModalOpen(true); setDrawerOpen(false); }}>拒绝审核</button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {modalOpen && modalAction && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">
              {modalAction.type === 'approve' ? '确认通过审核' : '拒绝审核'}
            </div>
            <div className="modal-body">
              {modalAction.type === 'approve' ? (
                <p>确定通过资源「{modalAction.resource.title}」的审核吗？</p>
              ) : (
                <div>
                  <p style={{ marginBottom: 12 }}>拒绝资源「{modalAction.resource.title}」的原因：</p>
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
                <button className="btn btn-primary" onClick={() => handleApprove(modalAction.resource.id)}>确认通过</button>
              ) : (
                <button className="btn btn-danger" onClick={() => handleReject(modalAction.resource.id, rejectReason || '不符合要求')}>确认拒绝</button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
