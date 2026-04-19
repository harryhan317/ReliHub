import { useState } from 'react';

interface FeedbackTicket {
  id: string;
  userId: string;
  nickname: string;
  type: string;
  subject: string;
  content: string;
  status: 'pending' | 'processing' | 'resolved' | 'rejected';
  createdAt: string;
  slaRemaining: string;
  handler?: string;
  reply?: string;
  internalNote?: string;
}

const MOCK_TICKETS: FeedbackTicket[] = [
  { id: 'FB-20260419-001', userId: 'U001', nickname: '张三', type: '功能异常', subject: 'AI对话无法发送消息', content: '点击发送按钮后没有反应，已经刷新页面重试多次', status: 'pending', createdAt: '2026-04-19 09:30', slaRemaining: '47h30m' },
  { id: 'FB-20260419-002', userId: 'U002', nickname: '李四', type: '体验建议', subject: '建议增加暗黑模式', content: '晚上使用时屏幕太亮，希望能支持暗黑模式切换', status: 'processing', createdAt: '2026-04-18 14:20', slaRemaining: '28h20m', handler: 'admin_01' },
  { id: 'FB-20260418-003', userId: 'U003', nickname: '王五', type: '内容纠错', subject: '资源描述与实际内容不符', content: '资源ID R-123的描述说是PDF格式，但下载后是Word文档', status: 'resolved', createdAt: '2026-04-17 10:15', slaRemaining: '-', handler: 'admin_01', reply: '已核实并更正资源描述，感谢反馈！', internalNote: '确实是格式标注错误' },
  { id: 'FB-20260418-004', userId: 'U004', nickname: '赵六', type: '其他', subject: '账号相关问题', content: '我之前的账号找不回来了', status: 'rejected', createdAt: '2026-04-16 16:40', slaRemaining: '-', handler: 'admin_02', reply: '请通过"忘记密码"功能使用手机号重置密码', internalNote: '用户未提供有效身份信息' },
  { id: 'FB-20260419-005', userId: 'U005', nickname: '钱七', type: '功能异常', subject: '签到功能无法使用', content: '点击签到按钮提示"网络异常"，但其他功能正常', status: 'pending', createdAt: '2026-04-19 08:00', slaRemaining: '46h00m' },
  { id: 'FB-20260419-006', userId: 'U006', nickname: '孙八', type: '体验建议', subject: '搜索功能优化建议', content: '搜索结果排序不够智能，希望能按相关度排序', status: 'processing', createdAt: '2026-04-18 11:30', slaRemaining: '31h30m', handler: 'admin_02' },
];

const STATUS_MAP: Record<string, { label: string; badge: string }> = {
  pending: { label: '待处理', badge: 'badge-warning' },
  processing: { label: '处理中', badge: 'badge-info' },
  resolved: { label: '已解决', badge: 'badge-success' },
  rejected: { label: '已驳回', badge: 'badge-error' },
};

const TYPE_OPTIONS = ['功能异常', '体验建议', '内容纠错', '其他'];

export default function FeedbackPage() {
  const [tickets, setTickets] = useState<FeedbackTicket[]>(MOCK_TICKETS);
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [searchText, setSearchText] = useState('');
  const [selectedTicket, setSelectedTicket] = useState<FeedbackTicket | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [internalNote, setInternalNote] = useState('');
  const [finalStatus, setFinalStatus] = useState<'resolved' | 'rejected'>('resolved');
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const filteredTickets = tickets.filter((t) => {
    if (statusFilter && t.status !== statusFilter) return false;
    if (typeFilter && t.type !== typeFilter) return false;
    if (searchText && !t.subject.includes(searchText) && !t.nickname.includes(searchText) && !t.id.includes(searchText)) return false;
    return true;
  });

  const handleOpenDetail = (ticket: FeedbackTicket) => {
    setSelectedTicket(ticket);
    setReplyText(ticket.reply || '');
    setInternalNote(ticket.internalNote || '');
    setFinalStatus('resolved');
    setDrawerOpen(true);
  };

  const handleProcess = () => {
    if (!replyText.trim()) {
      showToast('请填写处理结果描述', 'error');
      return;
    }
    if (selectedTicket) {
      setTickets((prev) => prev.map((t) =>
        t.id === selectedTicket.id
          ? { ...t, status: finalStatus, reply: replyText, internalNote, handler: 'current_admin' }
          : t
      ));
      showToast(`工单已标记为${finalStatus === 'resolved' ? '已解决' : '已驳回'}`, 'success');
      setDrawerOpen(false);
    }
  };

  const handleTakeTicket = (ticketId: string) => {
    setTickets((prev) => prev.map((t) =>
      t.id === ticketId && t.status === 'pending'
        ? { ...t, status: 'processing' as const, handler: 'current_admin' }
        : t
    ));
    showToast('已接单', 'success');
  };

  const statusOrder: Record<string, number> = { pending: 0, processing: 1, resolved: 2, rejected: 3 };
  const sortedTickets = [...filteredTickets].sort((a, b) => {
    const sa = statusOrder[a.status] ?? 9;
    const sb = statusOrder[b.status] ?? 9;
    if (sa !== sb) return sa - sb;
    return a.createdAt < b.createdAt ? -1 : 1;
  });

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}

      <div className="toolbar">
        <div className="toolbar-left">
          <select className="filter-select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">全部状态</option>
            <option value="pending">待处理</option>
            <option value="processing">处理中</option>
            <option value="resolved">已解决</option>
            <option value="rejected">已驳回</option>
          </select>
          <select className="filter-select" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            <option value="">全部类型</option>
            {TYPE_OPTIONS.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <div className="search-box">
            <span>🔍</span>
            <input placeholder="搜索工单号/标题/用户" value={searchText} onChange={(e) => setSearchText(e.target.value)} />
          </div>
        </div>
        <div className="toolbar-right">
          <button className="btn btn-sm" onClick={() => showToast('导出功能（对接后端API后实现）', 'success')}>📥 导出</button>
        </div>
      </div>

      <div style={{ padding: '8px 12px', background: '#fff7e6', borderRadius: 6, fontSize: 13, color: '#ad6800', marginBottom: 12 }}>
        ⏰ SLA规则：反馈工单需在48小时内处理完毕；超时自动提升优先级并向管理员发送提醒通知
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>工单编号</th>
            <th>提交用户</th>
            <th>反馈类型</th>
            <th>主题</th>
            <th>状态</th>
            <th>提交时间</th>
            <th>SLA剩余</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {sortedTickets.map((t) => {
            const statusInfo = STATUS_MAP[t.status] || { label: t.status, badge: 'badge-default' };
            return (
              <tr key={t.id} style={t.status === 'pending' ? { background: '#fffbe6' } : undefined}>
                <td style={{ fontWeight: 500, color: '#1890ff', cursor: 'pointer' }} onClick={() => handleOpenDetail(t)}>{t.id}</td>
                <td>{t.nickname}</td>
                <td><span className="badge badge-default">{t.type}</span></td>
                <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.subject}</td>
                <td><span className={`badge ${statusInfo.badge}`}>{statusInfo.label}</span></td>
                <td>{t.createdAt}</td>
                <td>
                  {t.slaRemaining !== '-' ? (
                    <span style={{ color: t.slaRemaining.startsWith('2') ? '#fa8c16' : '#52c41a', fontWeight: 500 }}>{t.slaRemaining}</span>
                  ) : '-'}
                </td>
                <td>
                  <div className="audit-action">
                    <button className="btn btn-sm" onClick={() => handleOpenDetail(t)}>详情</button>
                    {t.status === 'pending' && (
                      <button className="btn btn-primary btn-sm" onClick={() => handleTakeTicket(t.id)}>接单</button>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
          {sortedTickets.length === 0 && (
            <tr><td colSpan={8} style={{ textAlign: 'center', padding: 32, color: '#999' }}>暂无工单数据</td></tr>
          )}
        </tbody>
      </table>

      <div className={`overlay ${drawerOpen ? 'open' : ''}`} onClick={() => setDrawerOpen(false)} />
      <div className={`detail-drawer ${drawerOpen ? 'open' : ''}`}>
        <div className="detail-drawer-header">
          <div className="detail-drawer-title">工单详情</div>
          <div className="detail-drawer-close" onClick={() => setDrawerOpen(false)}>✕</div>
        </div>
        {selectedTicket && (
          <div className="detail-drawer-body">
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontWeight: 600, fontSize: 16 }}>{selectedTicket.id}</span>
                <span className={`badge ${(STATUS_MAP[selectedTicket.status] || { badge: 'badge-default' }).badge}`}>{(STATUS_MAP[selectedTicket.status] || { label: selectedTicket.status }).label}</span>
              </div>
              <div style={{ color: '#666', fontSize: 13 }}>
                提交用户：{selectedTicket.nickname} | 类型：{selectedTicket.type} | 提交时间：{selectedTicket.createdAt}
              </div>
            </div>

            <div style={{ marginBottom: 16 }}>
              <div style={{ fontWeight: 500, marginBottom: 4 }}>主题</div>
              <div>{selectedTicket.subject}</div>
            </div>

            <div style={{ marginBottom: 16 }}>
              <div style={{ fontWeight: 500, marginBottom: 4 }}>内容</div>
              <div style={{ padding: 12, background: '#f5f5f5', borderRadius: 6, lineHeight: 1.6 }}>{selectedTicket.content}</div>
            </div>

            {(selectedTicket.status === 'processing' || selectedTicket.status === 'pending') && (
              <>
                <div style={{ marginBottom: 12 }}>
                  <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>处理结果描述（必填）</label>
                  <textarea
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    style={{ width: '100%', marginTop: 4, padding: 8, border: '1px solid #d9d9d9', borderRadius: 6, minHeight: 80, fontSize: 13 }}
                    placeholder="填写处理结果..."
                  />
                </div>
                <div style={{ marginBottom: 12 }}>
                  <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>内部备注（可选，不对用户展示）</label>
                  <textarea
                    value={internalNote}
                    onChange={(e) => setInternalNote(e.target.value)}
                    style={{ width: '100%', marginTop: 4, padding: 8, border: '1px solid #d9d9d9', borderRadius: 6, minHeight: 60, fontSize: 13 }}
                    placeholder="内部备注..."
                  />
                </div>
                <div style={{ marginBottom: 16 }}>
                  <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>最终状态</label>
                  <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                      <input type="radio" name="finalStatus" checked={finalStatus === 'resolved'} onChange={() => setFinalStatus('resolved')} />
                      已解决
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                      <input type="radio" name="finalStatus" checked={finalStatus === 'rejected'} onChange={() => setFinalStatus('rejected')} />
                      已驳回
                    </label>
                  </div>
                </div>
                <button className="btn btn-primary" onClick={handleProcess} style={{ width: '100%' }}>提交处理结果</button>
              </>
            )}

            {selectedTicket.reply && (
              <div style={{ marginTop: 16, padding: 12, background: '#f6ffed', borderRadius: 6 }}>
                <div style={{ fontWeight: 500, marginBottom: 4, color: '#389e0d' }}>处理回复</div>
                <div style={{ lineHeight: 1.6 }}>{selectedTicket.reply}</div>
                {selectedTicket.internalNote && (
                  <div style={{ marginTop: 8, padding: 8, background: '#fffbe6', borderRadius: 4, fontSize: 12, color: '#ad6800' }}>
                    内部备注：{selectedTicket.internalNote}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
