import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';
import type { ResourceItem } from '@/types';

const statusMap: Record<string, { label: string; badge: string }> = {
  PENDING_REVIEW: { label: '待审核', badge: 'badge-warning' },
  APPROVED: { label: '已通过', badge: 'badge-success' },
  REJECTED: { label: '已拒绝', badge: 'badge-error' },
  BLOCKED: { label: '已封禁', badge: 'badge-error' },
  APPEALING: { label: '申诉中', badge: 'badge-info' },
  DUPLICATE_REVIEW: { label: '疑似重复', badge: 'badge-info' },
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
  const [modalAction, setModalAction] = useState<{ type: 'approve' | 'reject' | 'duplicate'; resource: ResourceItem } | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [batchModalOpen, setBatchModalOpen] = useState(false);
  const [batchAction, setBatchAction] = useState<'approve' | 'reject'>('approve');
  const [batchReason, setBatchReason] = useState('');
  const [duplicateModalOpen, setDuplicateModalOpen] = useState(false);
  const [duplicateResources, setDuplicateResources] = useState<ResourceItem[]>([]);

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

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === filteredResources.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredResources.map((r) => r.id)));
    }
  };

  const handleBatchAction = () => {
    if (selectedIds.size === 0) {
      showToast('请先选择资源', 'error');
      return;
    }
    setBatchModalOpen(true);
  };

  const executeBatch = () => {
    showToast(`批量${batchAction === 'approve' ? '通过' : '拒绝'} ${selectedIds.size} 条资源成功`, 'success');
    setSelectedIds(new Set());
    setBatchModalOpen(false);
    setBatchReason('');
    fetchResources();
  };

  const handleDuplicateReview = (resource: ResourceItem) => {
    setDuplicateResources([
      resource,
      { ...resource, id: resource.id + '_dup1', title: resource.title + '（副本A）', price: resource.price + 10 },
      { ...resource, id: resource.id + '_dup2', title: resource.title + '（副本B）', price: resource.price },
    ]);
    setDuplicateModalOpen(true);
  };

  const filteredResources = resources.filter((r) => {
    if (searchText && !r.title.includes(searchText)) return false;
    return true;
  });

  const formatDate = (d: string) => d ? d.slice(0, 16).replace('T', ' ') : '-';
  const totalPages = Math.ceil(total / 20);
  const pendingCount = resources.filter((r) => r.status === 'PENDING_REVIEW').length;

  const handleExport = () => {
    if (filteredResources.length === 0) {
      showToast('没有可导出的数据', 'error');
      return;
    }
    const headers = ['ID', '资源标题', '分类', '定价(可可豆)', '状态', '提交时间'];
    const rows = filteredResources.map((r) => [
      r.id,
      r.title,
      categoryMap[r.category_id] || r.category_id,
      r.price?.toString() || '0',
      statusMap[r.status]?.label || r.status,
      formatDate(r.created_at),
    ]);
    const csv = [headers, ...rows].map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `资源审核_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('导出成功', 'success');
  };

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
            <option value="DUPLICATE_REVIEW">疑似重复</option>
          </select>
          <div className="search-box">
            <span>🔍</span>
            <input placeholder="搜索资源标题/上传者" value={searchText} onChange={(e) => setSearchText(e.target.value)} />
          </div>
        </div>
        <div className="toolbar-right">
          {selectedIds.size > 0 && (
            <button className="btn btn-primary btn-sm" onClick={handleBatchAction}>
              批量操作（{selectedIds.size}）
            </button>
          )}
          <button className="btn btn-sm" onClick={handleExport}>📥 导出</button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 12, flexWrap: 'wrap' }}>
        <div style={{ padding: '6px 12px', background: '#fff7e6', borderRadius: 6, fontSize: 13, color: '#ad6800' }}>
          ⏰ SLA规则：资源审核需在24小时内处理完毕；超时自动提升优先级并通知管理员
        </div>
        <div style={{ padding: '6px 12px', background: '#f0f5ff', borderRadius: 6, fontSize: 13, color: '#1d39c4' }}>
          📋 待审核：{pendingCount} 条
        </div>
      </div>

      {loading ? (
        <div className="loading-spinner">加载中...</div>
      ) : (
        <>
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: 40 }}>
                  <input type="checkbox" checked={selectedIds.size === filteredResources.length && filteredResources.length > 0} onChange={toggleSelectAll} />
                </th>
                <th>ID</th><th>资源标题</th><th>分类</th><th>定价</th><th>状态</th><th>SLA</th><th>提交时间</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredResources.map((r) => {
                const slaHours = r.status === 'PENDING_REVIEW' ? Math.max(0, 24 - Math.floor((Date.now() - new Date(r.created_at).getTime()) / 3600000)) : null;
                const slaOverdue = slaHours !== null && slaHours <= 0;
                return (
                  <tr key={r.id} style={slaOverdue ? { background: '#fff1f0' } : undefined}>
                    <td>
                      <input type="checkbox" checked={selectedIds.has(r.id)} onChange={() => toggleSelect(r.id)} />
                    </td>
                    <td>{r.id.slice(0, 8)}</td>
                    <td>{r.title}</td>
                    <td>{categoryMap[r.category_id] || r.category_id}</td>
                    <td>{r.price > 0 ? `${r.price} 🫘` : '免费'}</td>
                    <td><span className={`badge ${statusMap[r.status]?.badge || 'badge-default'}`}>{statusMap[r.status]?.label || r.status}</span></td>
                    <td>
                      {slaHours !== null && (
                        <span style={{ color: slaOverdue ? '#ff4d4f' : slaHours <= 4 ? '#fa8c16' : '#52c41a', fontSize: 12, fontWeight: 500 }}>
                          {slaOverdue ? '⚠️ 已超时' : `${slaHours}h`}
                        </span>
                      )}
                      {slaHours === null && <span style={{ color: '#999' }}>-</span>}
                    </td>
                    <td>{formatDate(r.created_at)}</td>
                    <td>
                      <div className="audit-action">
                        {r.status === 'PENDING_REVIEW' && (
                          <>
                            <button className="btn btn-primary btn-sm" onClick={() => { setModalAction({ type: 'approve', resource: r }); setModalOpen(true); }}>通过</button>
                            <button className="btn btn-danger btn-sm" onClick={() => { setModalAction({ type: 'reject', resource: r }); setModalOpen(true); }}>拒绝</button>
                            <button className="btn btn-sm" onClick={() => handleDuplicateReview(r)}>疑似重复</button>
                          </>
                        )}
                        {r.status === 'APPEALING' && (
                          <button className="btn btn-primary btn-sm">处理申诉</button>
                        )}
                        {r.status === 'DUPLICATE_REVIEW' && (
                          <button className="btn btn-sm" onClick={() => handleDuplicateReview(r)}>重复审核</button>
                        )}
                        <button className="btn btn-sm" onClick={() => { setSelectedResource(r); setDrawerOpen(true); }}>详情</button>
                      </div>
                    </td>
                  </tr>
                );
              })}
              {filteredResources.length === 0 && (
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
                  <button className="btn" onClick={() => { handleDuplicateReview(selectedResource); setDrawerOpen(false); }}>疑似重复</button>
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
                    placeholder="请输入拒绝原因（必填）"
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

      {batchModalOpen && (
        <div className="modal-overlay" onClick={() => setBatchModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">批量{batchAction === 'approve' ? '通过' : '拒绝'}审核</div>
            <div className="modal-body">
              <p style={{ marginBottom: 12 }}>将对 {selectedIds.size} 条资源执行批量{batchAction === 'approve' ? '通过' : '拒绝'}操作</p>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>操作类型</label>
                <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                    <input type="radio" name="batchAction" checked={batchAction === 'approve'} onChange={() => setBatchAction('approve')} />
                    批量通过
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                    <input type="radio" name="batchAction" checked={batchAction === 'reject'} onChange={() => setBatchAction('reject')} />
                    批量拒绝
                  </label>
                </div>
              </div>
              {batchAction === 'reject' && (
                <div>
                  <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>拒绝原因（必填）</label>
                  <textarea
                    className="textarea-input"
                    value={batchReason}
                    onChange={(e) => setBatchReason(e.target.value)}
                    placeholder="请输入拒绝原因"
                    style={{ marginTop: 4 }}
                  />
                </div>
              )}
            </div>
            <div className="modal-actions">
              <button className="btn" onClick={() => setBatchModalOpen(false)}>取消</button>
              <button className={`btn ${batchAction === 'approve' ? 'btn-primary' : 'btn-danger'}`} onClick={executeBatch}>
                确认{batchAction === 'approve' ? '通过' : '拒绝'}
              </button>
            </div>
          </div>
        </div>
      )}

      {duplicateModalOpen && (
        <div className="modal-overlay" onClick={() => setDuplicateModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 800 }}>
            <div className="modal-title">疑似重复资源审核（三选一）</div>
            <div className="modal-body">
              <div style={{ padding: '8px 12px', background: '#fff7e6', borderRadius: 6, fontSize: 13, color: '#ad6800', marginBottom: 16 }}>
                ⚠️ 以下资源被AI判定为疑似重复，请选择保留其中一个，其余将被标记为重复下架
              </div>
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                {duplicateResources.map((r, idx) => (
                  <div key={r.id} style={{ flex: 1, minWidth: 200, border: '1px solid #d9d9d9', borderRadius: 8, padding: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <span style={{ fontWeight: 600 }}>候选 {idx + 1}</span>
                      <button className="btn btn-primary btn-sm" onClick={() => {
                        showToast(`已保留候选${idx + 1}，其余已下架`, 'success');
                        setDuplicateModalOpen(false);
                      }}>保留此版本</button>
                    </div>
                    <div style={{ fontSize: 13, color: '#666', lineHeight: 1.8 }}>
                      <div>ID: {r.id.slice(0, 8)}</div>
                      <div>标题: {r.title}</div>
                      <div>定价: {r.price > 0 ? `${r.price} 🫘` : '免费'}</div>
                      <div>分类: {categoryMap[r.category_id] || r.category_id}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
                <button className="btn" onClick={() => { showToast('已标记为非重复', 'success'); setDuplicateModalOpen(false); }}>非重复，全部保留</button>
                <button className="btn btn-danger btn-sm" onClick={() => { showToast('全部下架', 'success'); setDuplicateModalOpen(false); }}>全部下架</button>
              </div>
            </div>
            <div className="modal-actions">
              <button className="btn" onClick={() => setDuplicateModalOpen(false)}>关闭</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
