import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';
import type { TopicItem } from '@/types';

const statusMap: Record<string, { label: string; badge: string }> = {
  NORMAL: { label: '已通过', badge: 'badge-success' },
  PENDING: { label: '待审核', badge: 'badge-warning' },
  BLOCKED: { label: '已封禁', badge: 'badge-error' },
  REPORTED: { label: '举报待审', badge: 'badge-info' },
};

const categoryMap: Record<number, string> = {
  1: '标准规范',
  2: '社区话题',
  3: '应用笔记',
  4: '培训资料',
  5: '案例分享',
  6: '器件手册',
};

export default function AuditCommunityPage() {
  const [topics, setTopics] = useState<TopicItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [searchText, setSearchText] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState<TopicItem | null>(null);
  const [blockReason, setBlockReason] = useState('');
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchTopics = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminService.getTopics({
        status: statusFilter || undefined,
        page,
        page_size: 20,
      });
      setTopics(res.topics || []);
      setTotal(res.total);
    } catch {
      setTopics([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, page]);

  useEffect(() => { fetchTopics(); }, [fetchTopics]);

  const handleBlock = useCallback(async (topicId: string, reason: string) => {
    try {
      await adminService.blockTopic(topicId, reason);
      showToast('已封禁', 'success');
      fetchTopics();
    } catch {
      showToast('操作失败', 'error');
    }
    setModalOpen(false);
    setSelectedTopic(null);
    setBlockReason('');
  }, [fetchTopics]);

  const filteredTopics = topics.filter((t) => {
    if (searchText && !t.title.includes(searchText)) return false;
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
            <option value="PENDING">待审核</option>
            <option value="NORMAL">已通过</option>
            <option value="BLOCKED">已封禁</option>
          </select>
          <div className="search-box">
            <span>🔍</span>
            <input placeholder="搜索话题标题/作者" value={searchText} onChange={(e) => setSearchText(e.target.value)} />
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
                <th>ID</th><th>话题标题</th><th>分类</th><th>回复数</th><th>状态</th><th>发布时间</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredTopics.map((t) => (
                <tr key={t.id}>
                  <td>{t.id.slice(0, 8)}</td>
                  <td>{t.title}</td>
                  <td>{categoryMap[t.category_id] || t.category_id}</td>
                  <td>{t.post_count}</td>
                  <td><span className={`badge ${statusMap[t.status]?.badge || 'badge-default'}`}>{statusMap[t.status]?.label || t.status}</span></td>
                  <td>{formatDate(t.created_at)}</td>
                  <td>
                    <div className="audit-action">
                      {t.status === 'NORMAL' && (
                        <button className="btn btn-danger btn-sm" onClick={() => { setSelectedTopic(t); setModalOpen(true); }}>封禁</button>
                      )}
                      {t.status === 'PENDING' && (
                        <>
                          <button className="btn btn-primary btn-sm">通过</button>
                          <button className="btn btn-danger btn-sm" onClick={() => { setSelectedTopic(t); setModalOpen(true); }}>封禁</button>
                        </>
                      )}
                      <button className="btn btn-sm">详情</button>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredTopics.length === 0 && (
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

      {modalOpen && selectedTopic && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">封禁话题</div>
            <div className="modal-body">
              <p style={{ marginBottom: 12 }}>封禁话题「{selectedTopic.title}」的原因：</p>
              <textarea
                className="textarea-input"
                value={blockReason}
                onChange={(e) => setBlockReason(e.target.value)}
                placeholder="请输入封禁原因"
              />
            </div>
            <div className="modal-actions">
              <button className="btn" onClick={() => setModalOpen(false)}>取消</button>
              <button className="btn btn-danger" onClick={() => handleBlock(selectedTopic.id, blockReason || '违规内容')}>确认封禁</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
