import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';
import type { AdminUser } from '@/types';

interface ExpertApplication {
  id: string;
  userId: string;
  nickname: string;
  phone: string;
  organization: string;
  position: string;
  specialty: string;
  certificateUrl: string;
  bio: string;
  status: 'pending' | 'approved' | 'rejected' | 'change_pending';
  appliedAt: string;
  reviewedAt?: string;
  reviewer?: string;
  rejectReason?: string;
  type: 'new' | 'change';
  changeFields?: string[];
}

const MOCK_APPLICATIONS: ExpertApplication[] = [
  { id: 'EA001', userId: 'U1001', nickname: '张专家', phone: '138****0001', organization: '中国可靠性研究所', position: '高级工程师', specialty: 'FMEA/FTA分析', certificateUrl: '/cert/ea001.pdf', bio: '15年可靠性工程经验', status: 'pending', appliedAt: '2026-04-19 10:00', type: 'new' },
  { id: 'EA002', userId: 'U1002', nickname: '李工', phone: '139****0002', organization: '华为技术有限公司', position: '可靠性总监', specialty: '环境试验/加速寿命', certificateUrl: '/cert/ea002.pdf', bio: '20年产品可靠性测试经验', status: 'pending', appliedAt: '2026-04-18 14:30', type: 'new' },
  { id: 'EA003', userId: 'U1003', nickname: '王博士', phone: '137****0003', organization: '清华大学', position: '副教授', specialty: '概率统计/贝叶斯分析', certificateUrl: '/cert/ea003.pdf', bio: '10年学术研究经验', status: 'approved', appliedAt: '2026-04-15 09:00', reviewedAt: '2026-04-16 10:30', reviewer: 'admin_01', type: 'new' },
  { id: 'EA004', userId: 'U1004', nickname: '赵工', phone: '136****0004', organization: '中车集团', position: '首席可靠性师', specialty: 'RAMS工程', certificateUrl: '/cert/ea004.pdf', bio: '18年轨道交通可靠性经验', status: 'rejected', appliedAt: '2026-04-14 16:00', reviewedAt: '2026-04-15 11:00', reviewer: 'admin_02', rejectReason: '资质证明材料不完整', type: 'new' },
  { id: 'EA005', userId: 'U1003', nickname: '王博士', phone: '137****0003', organization: '清华大学', position: '教授', specialty: '概率统计/贝叶斯分析/机器学习', certificateUrl: '/cert/ea005.pdf', bio: '12年学术研究经验，新增机器学习方向', status: 'change_pending', appliedAt: '2026-04-19 08:00', type: 'change', changeFields: ['position', 'specialty', 'bio'] },
];

const statusMap: Record<string, { label: string; badge: string }> = {
  pending: { label: '待审核', badge: 'badge-warning' },
  approved: { label: '已通过', badge: 'badge-success' },
  rejected: { label: '已拒绝', badge: 'badge-error' },
  change_pending: { label: '变更待审', badge: 'badge-info' },
};

export default function UserExpertPage() {
  const [applications, setApplications] = useState<ExpertApplication[]>(MOCK_APPLICATIONS);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedApp, setSelectedApp] = useState<ExpertApplication | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalAction, setModalAction] = useState<{ type: 'approve' | 'reject'; app: ExpertApplication } | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const filteredApps = applications.filter((a) => {
    if (statusFilter && a.status !== statusFilter) return false;
    if (searchText && !a.nickname.includes(searchText) && !a.organization.includes(searchText)) return false;
    return true;
  });

  const pendingCount = applications.filter((a) => a.status === 'pending').length;
  const changeCount = applications.filter((a) => a.status === 'change_pending').length;

  const handleApprove = (app: ExpertApplication) => {
    setApplications((prev) => prev.map((a) => a.id === app.id ? { ...a, status: 'approved' as const, reviewedAt: new Date().toISOString().slice(0, 16).replace('T', ' '), reviewer: 'current_admin' } : a));
    showToast(app.type === 'change' ? '资料变更已通过' : '专家认证已通过', 'success');
    setModalOpen(false);
    setDrawerOpen(false);
  };

  const handleReject = (app: ExpertApplication, reason: string) => {
    if (!reason.trim()) {
      showToast('请填写拒绝原因', 'error');
      return;
    }
    setApplications((prev) => prev.map((a) => a.id === app.id ? { ...a, status: 'rejected' as const, reviewedAt: new Date().toISOString().slice(0, 16).replace('T', ' '), reviewer: 'current_admin', rejectReason: reason } : a));
    showToast('已拒绝', 'success');
    setModalOpen(false);
    setRejectReason('');
    setDrawerOpen(false);
  };

  const TABS = ['认证申请队列', '资料变更审核'];

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
            {idx === 0 && pendingCount > 0 && <span style={{ marginLeft: 4, background: '#ff4d4f', color: '#fff', borderRadius: 8, padding: '0 6px', fontSize: 11 }}>{pendingCount}</span>}
            {idx === 1 && changeCount > 0 && <span style={{ marginLeft: 4, background: '#1890ff', color: '#fff', borderRadius: 8, padding: '0 6px', fontSize: 11 }}>{changeCount}</span>}
          </button>
        ))}
      </div>

      <div className="toolbar">
        <div className="toolbar-left">
          <select className="filter-select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">全部状态</option>
            <option value="pending">待审核</option>
            <option value="approved">已通过</option>
            <option value="rejected">已拒绝</option>
            {activeTab === 1 && <option value="change_pending">变更待审</option>}
          </select>
          <div className="search-box">
            <span>🔍</span>
            <input placeholder="搜索昵称/单位" value={searchText} onChange={(e) => setSearchText(e.target.value)} />
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 12, flexWrap: 'wrap' }}>
        <div style={{ padding: '6px 12px', background: '#fff7e6', borderRadius: 6, fontSize: 13, color: '#ad6800' }}>
          ⏰ SLA规则：专家认证申请需在48小时内审核完毕；资料变更需在24小时内审核
        </div>
        <div style={{ padding: '6px 12px', background: '#f0f5ff', borderRadius: 6, fontSize: 13, color: '#1d39c4' }}>
          📋 待审核认证：{pendingCount} | 待审核变更：{changeCount}
        </div>
      </div>

      {loading ? (
        <div className="loading-spinner">加载中...</div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>申请ID</th><th>昵称</th><th>单位</th><th>职务</th><th>专业方向</th><th>状态</th><th>申请时间</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            {filteredApps
              .filter((a) => activeTab === 0 ? a.type === 'new' : a.type === 'change')
              .map((a) => (
                <tr key={a.id} style={a.status === 'pending' || a.status === 'change_pending' ? { background: '#fffbe6' } : undefined}>
                  <td style={{ fontWeight: 500 }}>{a.id}</td>
                  <td>{a.nickname}</td>
                  <td>{a.organization}</td>
                  <td>{a.position}</td>
                  <td style={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.specialty}</td>
                  <td><span className={`badge ${statusMap[a.status]?.badge || 'badge-default'}`}>{statusMap[a.status]?.label || a.status}</span></td>
                  <td>{a.appliedAt}</td>
                  <td>
                    <div className="audit-action">
                      {(a.status === 'pending' || a.status === 'change_pending') && (
                        <>
                          <button className="btn btn-primary btn-sm" onClick={() => { setModalAction({ type: 'approve', app: a }); setModalOpen(true); }}>通过</button>
                          <button className="btn btn-danger btn-sm" onClick={() => { setModalAction({ type: 'reject', app: a }); setModalOpen(true); }}>拒绝</button>
                        </>
                      )}
                      <button className="btn btn-sm" onClick={() => { setSelectedApp(a); setDrawerOpen(true); }}>详情</button>
                    </div>
                  </td>
                </tr>
              ))}
            {filteredApps.filter((a) => activeTab === 0 ? a.type === 'new' : a.type === 'change').length === 0 && (
              <tr><td colSpan={8} style={{ textAlign: 'center', padding: 32, color: '#999' }}>暂无数据</td></tr>
            )}
          </tbody>
        </table>
      )}

      <div className={`overlay ${drawerOpen ? 'open' : ''}`} onClick={() => setDrawerOpen(false)} />
      <div className={`detail-drawer ${drawerOpen ? 'open' : ''}`}>
        <div className="detail-drawer-header">
          <div className="detail-drawer-title">{selectedApp?.type === 'change' ? '资料变更详情' : '认证申请详情'}</div>
          <div className="detail-drawer-close" onClick={() => setDrawerOpen(false)}>✕</div>
        </div>
        <div className="detail-drawer-body">
          {selectedApp && (
            <>
              <div className="detail-field"><div className="detail-field-label">申请ID</div><div className="detail-field-value">{selectedApp.id}</div></div>
              <div className="detail-field"><div className="detail-field-label">用户ID</div><div className="detail-field-value">{selectedApp.userId}</div></div>
              <div className="detail-field"><div className="detail-field-label">昵称</div><div className="detail-field-value">{selectedApp.nickname}</div></div>
              <div className="detail-field"><div className="detail-field-label">手机号</div><div className="detail-field-value" style={{ fontFamily: 'monospace' }}>{selectedApp.phone}</div></div>
              <div className="detail-field"><div className="detail-field-label">单位</div><div className="detail-field-value">{selectedApp.organization}</div></div>
              <div className="detail-field"><div className="detail-field-label">职务</div><div className="detail-field-value">{selectedApp.position}</div></div>
              <div className="detail-field"><div className="detail-field-label">专业方向</div><div className="detail-field-value">{selectedApp.specialty}</div></div>
              <div className="detail-field"><div className="detail-field-label">个人简介</div><div className="detail-field-value">{selectedApp.bio}</div></div>
              <div className="detail-field"><div className="detail-field-label">资质证明</div><div className="detail-field-value">
                <a href={selectedApp.certificateUrl} target="_blank" rel="noreferrer" style={{ color: '#1890ff' }}>查看证明文件</a>
              </div></div>
              <div className="detail-field"><div className="detail-field-label">状态</div><div className="detail-field-value"><span className={`badge ${statusMap[selectedApp.status]?.badge}`}>{statusMap[selectedApp.status]?.label || selectedApp.status}</span></div></div>
              <div className="detail-field"><div className="detail-field-label">申请时间</div><div className="detail-field-value">{selectedApp.appliedAt}</div></div>
              {selectedApp.reviewedAt && <div className="detail-field"><div className="detail-field-label">审核时间</div><div className="detail-field-value">{selectedApp.reviewedAt}</div></div>}
              {selectedApp.reviewer && <div className="detail-field"><div className="detail-field-label">审核人</div><div className="detail-field-value">{selectedApp.reviewer}</div></div>}
              {selectedApp.rejectReason && <div className="detail-field"><div className="detail-field-label">拒绝原因</div><div className="detail-field-value" style={{ color: '#ff4d4f' }}>{selectedApp.rejectReason}</div></div>}

              {selectedApp.type === 'change' && selectedApp.changeFields && (
                <div style={{ marginTop: 16, padding: '8px 12px', background: '#f0f5ff', borderRadius: 6, fontSize: 13, color: '#1d39c4' }}>
                  📋 变更字段：{selectedApp.changeFields.join('、')}
                </div>
              )}

              {(selectedApp.status === 'pending' || selectedApp.status === 'change_pending') && (
                <div style={{ marginTop: 20, display: 'flex', gap: 8 }}>
                  <button className="btn btn-primary" onClick={() => handleApprove(selectedApp)}>
                    {selectedApp.type === 'change' ? '通过变更' : '通过认证'}
                  </button>
                  <button className="btn btn-danger" onClick={() => { setModalAction({ type: 'reject', app: selectedApp }); setModalOpen(true); }}>
                    拒绝
                  </button>
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
              {modalAction.type === 'approve' ? `确认${modalAction.app.type === 'change' ? '通过变更' : '通过认证'}` : '拒绝申请'}
            </div>
            <div className="modal-body">
              {modalAction.type === 'approve' ? (
                <div>
                  <p>确定{modalAction.app.type === 'change' ? '通过「' + modalAction.app.nickname + '」的资料变更申请' : '通过「' + modalAction.app.nickname + '」的专家认证申请'}吗？</p>
                  {modalAction.app.type === 'change' && modalAction.app.changeFields && (
                    <div style={{ padding: '8px 12px', background: '#f0f5ff', borderRadius: 6, fontSize: 13, color: '#1d39c4', marginTop: 8 }}>
                      变更字段：{modalAction.app.changeFields.join('、')}
                    </div>
                  )}
                </div>
              ) : (
                <div>
                  <p style={{ marginBottom: 12 }}>拒绝「{modalAction.app.nickname}」{modalAction.app.type === 'change' ? '的资料变更' : '的专家认证'}申请的原因：</p>
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
              <button className="btn" onClick={() => { setModalOpen(false); setRejectReason(''); }}>取消</button>
              {modalAction.type === 'approve' ? (
                <button className="btn btn-primary" onClick={() => handleApprove(modalAction.app)}>确认通过</button>
              ) : (
                <button className="btn btn-danger" onClick={() => handleReject(modalAction.app, rejectReason)}>确认拒绝</button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
