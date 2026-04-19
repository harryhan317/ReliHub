import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';
import type { TopicItem } from '@/types';

const statusMap: Record<string, { label: string; badge: string }> = {
  NORMAL: { label: '已通过', badge: 'badge-success' },
  PENDING: { label: '待审核', badge: 'badge-warning' },
  BLOCKED: { label: '已封禁', badge: 'badge-error' },
  REPORTED: { label: '举报待审', badge: 'badge-info' },
  AI_FLAGGED: { label: 'AI可疑', badge: 'badge-warning' },
};

const categoryMap: Record<number, string> = {
  1: '标准规范',
  2: '社区话题',
  3: '应用笔记',
  4: '培训资料',
  5: '案例分享',
  6: '器件手册',
};

interface ReportRecord {
  id: string;
  reporterId: string;
  reporterName: string;
  reason: string;
  detail: string;
  createdAt: string;
}

interface CommentItem {
  id: string;
  topicId: string;
  topicTitle: string;
  author: string;
  content: string;
  status: 'normal' | 'pending' | 'blocked' | 'ai_flagged';
  createdAt: string;
}

const MOCK_REPORTS: ReportRecord[] = [
  { id: 'RPT001', reporterId: 'U1001', reporterName: '张三', reason: '虚假信息', detail: '该话题包含未经证实的数据', createdAt: '2026-04-19 10:30' },
  { id: 'RPT002', reporterId: 'U1002', reporterName: '李四', reason: '广告推广', detail: '内容中包含商业推广链接', createdAt: '2026-04-19 11:20' },
  { id: 'RPT003', reporterId: 'U1003', reporterName: '王五', reason: '人身攻击', detail: '回复中使用侮辱性语言', createdAt: '2026-04-18 16:45' },
];

const MOCK_COMMENTS: CommentItem[] = [
  { id: 'C001', topicId: 'T001', topicTitle: '可靠性设计规范讨论', author: '用户A', content: '这个规范已经过时了，建议更新', status: 'normal', createdAt: '2026-04-19 09:00' },
  { id: 'C002', topicId: 'T002', topicTitle: 'FMEA分析方法', author: '用户B', content: '加微信xxx获取完整资料', status: 'ai_flagged', createdAt: '2026-04-19 10:15' },
  { id: 'C003', topicId: 'T001', topicTitle: '可靠性设计规范讨论', author: '用户C', content: '楼主说的不对，你根本不懂', status: 'pending', createdAt: '2026-04-19 11:30' },
];

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

  const [activeTab, setActiveTab] = useState(0);
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState<ReportRecord | null>(null);
  const [commentModalOpen, setCommentModalOpen] = useState(false);
  const [selectedComment, setSelectedComment] = useState<CommentItem | null>(null);

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

  const TABS = ['话题审核', '举报处理', '点评审核'];

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}

      <div style={{ display: 'flex', gap: 0, marginBottom: 16 }}>
        {TABS.map((tab, idx) => (
          <button
            key={tab}
            className={`btn btn-sm ${activeTab === idx ? 'btn-primary' : ''}`}
            onClick={() => setActiveTab(idx)}
            style={{ borderRadius: idx === 0 ? '6px 0 0 6px' : idx === TABS.length - 1 ? '0 6px 6px 0' : '0' }}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 0 && (
        <>
          <div className="toolbar">
            <div className="toolbar-left">
              <select className="filter-select" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
                <option value="">全部状态</option>
                <option value="PENDING">待审核</option>
                <option value="NORMAL">已通过</option>
                <option value="BLOCKED">已封禁</option>
                <option value="AI_FLAGGED">AI可疑</option>
              </select>
              <div className="search-box">
                <span>🔍</span>
                <input placeholder="搜索话题标题/作者" value={searchText} onChange={(e) => setSearchText(e.target.value)} />
              </div>
            </div>
            <div className="toolbar-right">
              <button className="btn btn-sm">📥 导出</button>
            </div>
          </div>

          <div style={{ padding: '6px 12px', background: '#fff7e6', borderRadius: 6, fontSize: 13, color: '#ad6800', marginBottom: 12 }}>
            ⏰ SLA规则：社区内容审核需在12小时内处理完毕；AI可疑内容需在4小时内优先处理
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
                    <tr key={t.id} style={t.status === 'AI_FLAGGED' ? { background: '#fffbe6' } : undefined}>
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
                              <button className="btn btn-primary btn-sm" onClick={() => { showToast('已通过', 'success'); fetchTopics(); }}>通过</button>
                              <button className="btn btn-danger btn-sm" onClick={() => { setSelectedTopic(t); setModalOpen(true); }}>封禁</button>
                            </>
                          )}
                          {t.status === 'AI_FLAGGED' && (
                            <>
                              <button className="btn btn-primary btn-sm" onClick={() => { showToast('已通过（AI误判）', 'success'); fetchTopics(); }}>通过</button>
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
        </>
      )}

      {activeTab === 1 && (
        <>
          <div className="toolbar">
            <div className="toolbar-left">
              <div className="search-box">
                <span>🔍</span>
                <input placeholder="搜索举报内容/举报人" value={searchText} onChange={(e) => setSearchText(e.target.value)} />
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 12, marginBottom: 12, flexWrap: 'wrap' }}>
            <div style={{ padding: '6px 12px', background: '#fff1f0', borderRadius: 6, fontSize: 13, color: '#cf1322' }}>
              🚨 待处理举报：{MOCK_REPORTS.length} 条
            </div>
            <div style={{ padding: '6px 12px', background: '#fff7e6', borderRadius: 6, fontSize: 13, color: '#ad6800' }}>
              ⏰ SLA规则：举报工单需在24小时内处理完毕
            </div>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>举报ID</th><th>举报人</th><th>举报原因</th><th>举报详情</th><th>举报时间</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_REPORTS.map((r) => (
                <tr key={r.id}>
                  <td style={{ fontWeight: 500 }}>{r.id}</td>
                  <td>{r.reporterName}</td>
                  <td><span className="badge badge-error">{r.reason}</span></td>
                  <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.detail}</td>
                  <td>{r.createdAt}</td>
                  <td>
                    <div className="audit-action">
                      <button className="btn btn-sm" onClick={() => { setSelectedReport(r); setReportModalOpen(true); }}>处理</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {reportModalOpen && selectedReport && (
            <div className="modal-overlay" onClick={() => setReportModalOpen(false)}>
              <div className="modal-card" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 560 }}>
                <div className="modal-title">处理举报</div>
                <div className="modal-body">
                  <div style={{ marginBottom: 12 }}>
                    <div style={{ fontSize: 13, color: '#666', lineHeight: 1.8 }}>
                      <div><strong>举报ID：</strong>{selectedReport.id}</div>
                      <div><strong>举报人：</strong>{selectedReport.reporterName}（{selectedReport.reporterId}）</div>
                      <div><strong>举报原因：</strong><span className="badge badge-error">{selectedReport.reason}</span></div>
                      <div><strong>举报详情：</strong>{selectedReport.detail}</div>
                      <div><strong>举报时间：</strong>{selectedReport.createdAt}</div>
                    </div>
                  </div>
                  <div style={{ padding: '8px 12px', background: '#f0f5ff', borderRadius: 6, fontSize: 13, color: '#1d39c4', marginBottom: 12 }}>
                    ℹ️ 举报查实后，系统将自动对被举报内容执行处置，并向举报人发送处理结果通知
                  </div>
                </div>
                <div className="modal-actions" style={{ justifyContent: 'flex-start' }}>
                  <button className="btn btn-danger btn-sm" onClick={() => { showToast('举报成立，内容已封禁', 'success'); setReportModalOpen(false); }}>举报成立（封禁内容）</button>
                  <button className="btn btn-sm" onClick={() => { showToast('举报不成立，已驳回', 'success'); setReportModalOpen(false); }}>举报不成立</button>
                  <button className="btn btn-sm" onClick={() => setReportModalOpen(false)}>关闭</button>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {activeTab === 2 && (
        <>
          <div className="toolbar">
            <div className="toolbar-left">
              <select className="filter-select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                <option value="">全部状态</option>
                <option value="pending">待审核</option>
                <option value="ai_flagged">AI可疑</option>
                <option value="normal">正常</option>
                <option value="blocked">已封禁</option>
              </select>
              <div className="search-box">
                <span>🔍</span>
                <input placeholder="搜索点评内容/作者" value={searchText} onChange={(e) => setSearchText(e.target.value)} />
              </div>
            </div>
          </div>

          <div style={{ padding: '6px 12px', background: '#f0f5ff', borderRadius: 6, fontSize: 13, color: '#1d39c4', marginBottom: 12 }}>
            📝 点评审核：对社区话题下的回复/点评内容进行审核，AI可疑内容需优先处理
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th><th>所属话题</th><th>作者</th><th>内容</th><th>状态</th><th>时间</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_COMMENTS.map((c) => (
                <tr key={c.id} style={c.status === 'ai_flagged' ? { background: '#fffbe6' } : undefined}>
                  <td>{c.id}</td>
                  <td style={{ maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.topicTitle}</td>
                  <td>{c.author}</td>
                  <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.content}</td>
                  <td>
                    <span className={`badge ${c.status === 'ai_flagged' ? 'badge-warning' : c.status === 'pending' ? 'badge-warning' : c.status === 'blocked' ? 'badge-error' : 'badge-success'}`}>
                      {c.status === 'ai_flagged' ? 'AI可疑' : c.status === 'pending' ? '待审核' : c.status === 'blocked' ? '已封禁' : '正常'}
                    </span>
                  </td>
                  <td>{c.createdAt}</td>
                  <td>
                    <div className="audit-action">
                      {(c.status === 'pending' || c.status === 'ai_flagged') && (
                        <>
                          <button className="btn btn-primary btn-sm" onClick={() => { showToast('点评已通过', 'success'); }}>通过</button>
                          <button className="btn btn-danger btn-sm" onClick={() => { setSelectedComment(c); setCommentModalOpen(true); }}>封禁</button>
                        </>
                      )}
                      <button className="btn btn-sm" onClick={() => { setSelectedComment(c); setCommentModalOpen(true); }}>详情</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {commentModalOpen && selectedComment && (
            <div className="modal-overlay" onClick={() => setCommentModalOpen(false)}>
              <div className="modal-card" onClick={(e) => e.stopPropagation()}>
                <div className="modal-title">点评详情</div>
                <div className="modal-body">
                  <div style={{ fontSize: 13, color: '#666', lineHeight: 1.8 }}>
                    <div><strong>ID：</strong>{selectedComment.id}</div>
                    <div><strong>所属话题：</strong>{selectedComment.topicTitle}</div>
                    <div><strong>作者：</strong>{selectedComment.author}</div>
                    <div><strong>内容：</strong></div>
                    <div style={{ padding: '8px 12px', background: '#f5f5f5', borderRadius: 6, marginTop: 4 }}>{selectedComment.content}</div>
                    <div style={{ marginTop: 8 }}><strong>状态：</strong>
                      <span className={`badge ${selectedComment.status === 'ai_flagged' ? 'badge-warning' : selectedComment.status === 'pending' ? 'badge-warning' : selectedComment.status === 'blocked' ? 'badge-error' : 'badge-success'}`}>
                        {selectedComment.status === 'ai_flagged' ? 'AI可疑' : selectedComment.status === 'pending' ? '待审核' : selectedComment.status === 'blocked' ? '已封禁' : '正常'}
                      </span>
                    </div>
                    <div><strong>时间：</strong>{selectedComment.createdAt}</div>
                  </div>
                </div>
                <div className="modal-actions">
                  {(selectedComment.status === 'pending' || selectedComment.status === 'ai_flagged') && (
                    <>
                      <button className="btn btn-primary btn-sm" onClick={() => { showToast('点评已通过', 'success'); setCommentModalOpen(false); }}>通过</button>
                      <button className="btn btn-danger btn-sm" onClick={() => { showToast('点评已封禁', 'success'); setCommentModalOpen(false); }}>封禁</button>
                    </>
                  )}
                  <button className="btn btn-sm" onClick={() => setCommentModalOpen(false)}>关闭</button>
                </div>
              </div>
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
                placeholder="请输入封禁原因（必填）"
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
