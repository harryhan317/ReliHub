import { useState } from 'react';

interface AdminAccount {
  id: string;
  username: string;
  realName: string;
  phone: string;
  role: 'SUPER_ADMIN' | 'ADMIN';
  status: 'active' | 'frozen';
  lastLoginAt: string;
  createdAt: string;
}

const MOCK_ADMINS: AdminAccount[] = [
  { id: 'A001', username: 'super_admin', realName: '系统管理员', phone: '138****0001', role: 'SUPER_ADMIN', status: 'active', lastLoginAt: '2026-04-19 09:30', createdAt: '2026-01-01' },
  { id: 'A002', username: 'admin_01', realName: '张运营', phone: '139****0002', role: 'ADMIN', status: 'active', lastLoginAt: '2026-04-19 08:15', createdAt: '2026-02-15' },
  { id: 'A003', username: 'admin_02', realName: '李审核', phone: '137****0003', role: 'ADMIN', status: 'active', lastLoginAt: '2026-04-18 17:40', createdAt: '2026-03-01' },
  { id: 'A004', username: 'admin_03', realName: '王客服', phone: '136****0004', role: 'ADMIN', status: 'frozen', lastLoginAt: '2026-04-10 14:20', createdAt: '2026-03-20' },
];

export default function AdminAccountPage() {
  const [admins, setAdmins] = useState<AdminAccount[]>(MOCK_ADMINS);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDetailDrawer, setShowDetailDrawer] = useState(false);
  const [selectedAdmin, setSelectedAdmin] = useState<AdminAccount | null>(null);
  const [showConfirmModal, setShowConfirmModal] = useState<{ type: 'freeze' | 'delete' | 'resetPwd'; admin: AdminAccount } | null>(null);
  const [confirmReason, setConfirmReason] = useState('');
  const [showTransferModal, setShowTransferModal] = useState<AdminAccount | null>(null);
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const [newUsername, setNewUsername] = useState('');
  const [newRealName, setNewRealName] = useState('');
  const [newPhone, setNewPhone] = useState('');
  const [newRole, setNewRole] = useState<'SUPER_ADMIN' | 'ADMIN'>('ADMIN');

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleAdd = () => {
    if (!newUsername.trim() || !newRealName.trim() || !newPhone.trim()) {
      showToast('请填写完整信息', 'error');
      return;
    }
    const newAdmin: AdminAccount = {
      id: `A${String(Date.now()).slice(-4)}`,
      username: newUsername.trim(),
      realName: newRealName.trim(),
      phone: newPhone.trim().slice(0, 3) + '****' + newPhone.trim().slice(-4),
      role: newRole,
      status: 'active',
      lastLoginAt: '-',
      createdAt: new Date().toISOString().slice(0, 10),
    };
    setAdmins((prev) => [...prev, newAdmin]);
    setShowAddModal(false);
    setNewUsername('');
    setNewRealName('');
    setNewPhone('');
    setNewRole('ADMIN');
    showToast('管理员账号已创建，初始密码已发送至手机号', 'success');
  };

  const handleFreeze = (admin: AdminAccount) => {
    const activeSuperAdmins = admins.filter((a) => a.role === 'SUPER_ADMIN' && a.status === 'active');
    if (admin.role === 'SUPER_ADMIN' && activeSuperAdmins.length <= 1) {
      showToast('禁止冻结最后一名超级管理员', 'error');
      return;
    }
    setShowConfirmModal({ type: 'freeze', admin });
  };

  const handleDelete = (admin: AdminAccount) => {
    const activeSuperAdmins = admins.filter((a) => a.role === 'SUPER_ADMIN' && a.status === 'active');
    if (admin.role === 'SUPER_ADMIN' && activeSuperAdmins.length <= 1) {
      showToast('禁止删除最后一名超级管理员', 'error');
      return;
    }
    setShowConfirmModal({ type: 'delete', admin });
  };

  const executeConfirm = () => {
    if (!showConfirmModal) return;
    if (!confirmReason.trim()) {
      showToast('请填写操作原因', 'error');
      return;
    }
    const { type, admin } = showConfirmModal;
    if (type === 'freeze') {
      setAdmins((prev) => prev.map((a) => a.id === admin.id ? { ...a, status: 'frozen' as const } : a));
      showToast('账号已冻结', 'success');
    } else if (type === 'delete') {
      setAdmins((prev) => prev.filter((a) => a.id !== admin.id));
      showToast('账号已删除', 'success');
    } else if (type === 'resetPwd') {
      showToast('密码已重置，新密码已发送至管理员手机号', 'success');
    }
    setShowConfirmModal(null);
    setConfirmReason('');
  };

  const activeSuperAdminCount = admins.filter((a) => a.role === 'SUPER_ADMIN' && a.status === 'active').length;

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}

      <div className="toolbar">
        <div className="toolbar-left">
          <div style={{ padding: '4px 12px', background: '#f0f5ff', borderRadius: 6, fontSize: 13, color: '#1d39c4' }}>
            超级管理员：{activeSuperAdminCount} 名（活跃） | 管理员：{admins.filter((a) => a.role === 'ADMIN' && a.status === 'active').length} 名（活跃）
          </div>
        </div>
        <div className="toolbar-right">
          <button className="btn btn-primary btn-sm" onClick={() => setShowAddModal(true)}>➕ 新增管理员</button>
        </div>
      </div>

      <div style={{ padding: '8px 12px', background: '#fff1f0', borderRadius: 6, fontSize: 13, color: '#cf1322', marginBottom: 12 }}>
        ⚠️ 系统硬约束：禁止冻结/删除平台最后一名状态正常的超级管理员账号 | 所有操作均记录入操作日志
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>账号名</th>
            <th>姓名</th>
            <th>手机号（脱敏）</th>
            <th>角色</th>
            <th>状态</th>
            <th>最近登录</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {admins.map((admin) => (
            <tr key={admin.id} style={admin.status === 'frozen' ? { background: '#f5f5f5' } : undefined}>
              <td style={{ fontWeight: 500 }}>{admin.username}</td>
              <td>{admin.realName}</td>
              <td style={{ fontFamily: 'monospace' }}>{admin.phone}</td>
              <td>
                <span className={`badge ${admin.role === 'SUPER_ADMIN' ? 'badge-error' : 'badge-info'}`}>
                  {admin.role === 'SUPER_ADMIN' ? '超级管理员' : '管理员'}
                </span>
              </td>
              <td>
                <span className={`badge ${admin.status === 'active' ? 'badge-success' : 'badge-error'}`}>
                  {admin.status === 'active' ? '正常' : '冻结'}
                </span>
              </td>
              <td>{admin.lastLoginAt}</td>
              <td>{admin.createdAt}</td>
              <td>
                <div className="audit-action">
                  <button className="btn btn-sm" onClick={() => { setSelectedAdmin(admin); setShowDetailDrawer(true); }}>详情</button>
                  {admin.status === 'active' && (
                    <button className="btn btn-sm" onClick={() => handleFreeze(admin)}>冻结</button>
                  )}
                  {admin.status === 'frozen' && (
                    <>
                      <button className="btn btn-sm" style={{ color: '#52c41a' }} onClick={() => {
                        setAdmins((prev) => prev.map((a) => a.id === admin.id ? { ...a, status: 'active' as const } : a));
                        showToast('账号已解冻', 'success');
                      }}>解冻</button>
                      <button className="btn btn-sm" onClick={() => setShowTransferModal(admin)}>批量转派</button>
                    </>
                  )}
                  <button className="btn btn-sm" onClick={() => setShowConfirmModal({ type: 'resetPwd', admin })}>重置密码</button>
                  <button className="btn btn-sm" style={{ color: '#ff4d4f' }} onClick={() => handleDelete(admin)}>删除</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showAddModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1001, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', borderRadius: 12, padding: 24, width: 480 }}>
            <h3 style={{ margin: '0 0 16px' }}>➕ 新增管理员</h3>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>管理员账号名（唯一，不可重复）</label>
              <input className="config-input" type="text" value={newUsername} onChange={(e) => setNewUsername(e.target.value)} style={{ width: '100%', marginTop: 4 }} placeholder="输入账号名" />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>真实姓名</label>
              <input className="config-input" type="text" value={newRealName} onChange={(e) => setNewRealName(e.target.value)} style={{ width: '100%', marginTop: 4 }} placeholder="输入真实姓名" />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>手机号（用于短信验证和紧急联系）</label>
              <input className="config-input" type="text" value={newPhone} onChange={(e) => setNewPhone(e.target.value)} style={{ width: '100%', marginTop: 4 }} placeholder="输入手机号" />
            </div>
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>角色</label>
              <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                  <input type="radio" name="newRole" checked={newRole === 'ADMIN'} onChange={() => setNewRole('ADMIN')} />
                  管理员
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                  <input type="radio" name="newRole" checked={newRole === 'SUPER_ADMIN'} onChange={() => setNewRole('SUPER_ADMIN')} />
                  超级管理员
                </label>
              </div>
            </div>
            <div style={{ padding: '8px 12px', background: '#f0f5ff', borderRadius: 6, fontSize: 12, color: '#1d39c4', marginBottom: 16 }}>
              ℹ️ 系统将自动生成初始密码（12位含大小写+数字+特殊字符）并发送至管理员手机号，首次登录强制修改密码。
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button className="btn btn-sm" onClick={() => setShowAddModal(false)}>取消</button>
              <button className="btn btn-primary btn-sm" onClick={handleAdd}>确认创建</button>
            </div>
          </div>
        </div>
      )}

      {showConfirmModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1002, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', borderRadius: 12, padding: 24, width: 420 }}>
            <h3 style={{ margin: '0 0 12px' }}>
              {showConfirmModal.type === 'freeze' ? '⚠️ 确认冻结' : showConfirmModal.type === 'delete' ? '🔴 确认删除' : '🔑 确认重置密码'}
            </h3>
            <p style={{ margin: '0 0 12px', color: '#666' }}>
              {showConfirmModal.type === 'freeze' && `确定要冻结账号 "${showConfirmModal.admin.username}" 吗？冻结后该账号无法登录。`}
              {showConfirmModal.type === 'delete' && `确定要永久删除账号 "${showConfirmModal.admin.username}" 吗？此操作不可逆。`}
              {showConfirmModal.type === 'resetPwd' && `确定要重置账号 "${showConfirmModal.admin.username}" 的密码吗？重置后旧Token立即失效。`}
            </p>
            {showConfirmModal.type === 'delete' && (
              <div style={{ marginBottom: 12, padding: '8px 12px', background: '#fff7e6', borderRadius: 6, fontSize: 13, color: '#ad6800' }}>
                📋 删除前需将该账号名下全部待审、待办任务转移至指定人
              </div>
            )}
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>操作原因（必填）</label>
              <input className="config-input" type="text" value={confirmReason} onChange={(e) => setConfirmReason(e.target.value)} style={{ width: '100%', marginTop: 4 }} placeholder="请输入操作原因" />
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button className="btn btn-sm" onClick={() => { setShowConfirmModal(null); setConfirmReason(''); }}>取消</button>
              <button className="btn btn-sm" style={{ background: showConfirmModal.type === 'delete' ? '#ff4d4f' : '#1890ff', color: '#fff' }} onClick={executeConfirm}>
                确认{showConfirmModal.type === 'freeze' ? '冻结' : showConfirmModal.type === 'delete' ? '删除' : '重置'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showTransferModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1002, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', borderRadius: 12, padding: 24, width: 420 }}>
            <h3 style={{ margin: '0 0 12px' }}>📋 批量转派任务</h3>
            <p style={{ margin: '0 0 12px', color: '#666' }}>
              将账号 "{showTransferModal.username}" 下所有待处理任务转移至指定管理员
            </p>
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>目标管理员</label>
              <select className="config-input" style={{ width: '100%', marginTop: 4 }} defaultValue="">
                <option value="">请选择目标管理员</option>
                {admins.filter((a) => a.id !== showTransferModal.id && a.status === 'active').map((a) => (
                  <option key={a.id} value={a.id}>{a.realName}（{a.username}）</option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button className="btn btn-sm" onClick={() => setShowTransferModal(null)}>取消</button>
              <button className="btn btn-primary btn-sm" onClick={() => { setShowTransferModal(null); showToast('任务已转派', 'success'); }}>确认转派</button>
            </div>
          </div>
        </div>
      )}

      <div className={`overlay ${showDetailDrawer ? 'open' : ''}`} onClick={() => setShowDetailDrawer(false)} />
      <div className={`detail-drawer ${showDetailDrawer ? 'open' : ''}`}>
        <div className="detail-drawer-header">
          <div className="detail-drawer-title">管理员详情</div>
          <div className="detail-drawer-close" onClick={() => setShowDetailDrawer(false)}>✕</div>
        </div>
        {selectedAdmin && (
          <div className="detail-drawer-body">
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                <div style={{ width: 48, height: 48, borderRadius: '50%', background: selectedAdmin.role === 'SUPER_ADMIN' ? '#ff4d4f' : '#1890ff', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, fontWeight: 600 }}>
                  {selectedAdmin.realName.slice(0, 1)}
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 16 }}>{selectedAdmin.realName}</div>
                  <div style={{ color: '#999', fontSize: 13 }}>@{selectedAdmin.username}</div>
                </div>
              </div>
            </div>

            <div style={{ marginBottom: 16 }}>
              <h4 style={{ fontSize: 14, margin: '0 0 8px' }}>基本信息</h4>
              <div className="config-row"><div className="config-label">账号名</div><div className="config-value">{selectedAdmin.username}</div></div>
              <div className="config-row"><div className="config-label">姓名</div><div className="config-value">{selectedAdmin.realName}</div></div>
              <div className="config-row"><div className="config-label">手机号</div><div className="config-value" style={{ fontFamily: 'monospace' }}>{selectedAdmin.phone}</div></div>
              <div className="config-row"><div className="config-label">角色</div><div className="config-value"><span className={`badge ${selectedAdmin.role === 'SUPER_ADMIN' ? 'badge-error' : 'badge-info'}`}>{selectedAdmin.role === 'SUPER_ADMIN' ? '超级管理员' : '管理员'}</span></div></div>
              <div className="config-row"><div className="config-label">状态</div><div className="config-value"><span className={`badge ${selectedAdmin.status === 'active' ? 'badge-success' : 'badge-error'}`}>{selectedAdmin.status === 'active' ? '正常' : '冻结'}</span></div></div>
              <div className="config-row"><div className="config-label">最近登录</div><div className="config-value">{selectedAdmin.lastLoginAt}</div></div>
              <div className="config-row"><div className="config-label">创建时间</div><div className="config-value">{selectedAdmin.createdAt}</div></div>
            </div>

            <div>
              <h4 style={{ fontSize: 14, margin: '0 0 8px' }}>权限矩阵</h4>
              <table className="data-table" style={{ boxShadow: 'none' }}>
                <thead><tr><th>功能</th><th style={{ textAlign: 'center' }}>权限</th></tr></thead>
                <tbody>
                  {[
                    { label: '内容审核', has: true },
                    { label: '用户列表查看', has: true },
                    { label: '用户违规处置', has: selectedAdmin.role === 'SUPER_ADMIN' },
                    { label: '安全日志查看', has: true },
                    { label: '参数配置', has: selectedAdmin.role === 'SUPER_ADMIN' },
                    { label: '管理员账号管理', has: selectedAdmin.role === 'SUPER_ADMIN' },
                    { label: '反爬/反刷规则配置', has: selectedAdmin.role === 'SUPER_ADMIN' },
                    { label: '限流配置', has: selectedAdmin.role === 'SUPER_ADMIN' },
                  ].map((row) => (
                    <tr key={row.label}>
                      <td>{row.label}</td>
                      <td style={{ textAlign: 'center' }}>{row.has ? '✅' : '❌'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
