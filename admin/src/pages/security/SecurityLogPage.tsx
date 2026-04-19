import { useState, useEffect } from 'react';
import { adminService } from '@/services/adminService';

interface OperationLog {
  id: string;
  operator_id: string;
  operator_role: string;
  operation_time: string;
  operation_type: string;
  description: string;
  before_value: string;
  after_value: string;
}

const OPERATION_TYPES = ['配置变更', '审核操作', '用户处置', '管理员账号管理', '其他'];
const LOG_TYPE_TABS = ['操作日志', '登录日志'];

const MOCK_OPERATION_LOGS: OperationLog[] = [
  { id: '1', operator_id: 'superadmin', operator_role: '超级管理员', operation_time: '2026-04-19 10:30:00', operation_type: '配置变更', description: '修改AI问答等级权益配置-新兵每日会话上限', before_value: '5', after_value: '8' },
  { id: '2', operator_id: 'admin01', operator_role: '管理员', operation_time: '2026-04-19 09:15:00', operation_type: '审核操作', description: '通过资源审核：资源ID#1024', before_value: '待审核', after_value: '已通过' },
  { id: '3', operator_id: 'superadmin', operator_role: '超级管理员', operation_time: '2026-04-18 16:45:00', operation_type: '用户处置', description: '临时封禁用户 user_005（7天）', before_value: '正常', after_value: '临时封禁' },
  { id: '4', operator_id: 'superadmin', operator_role: '超级管理员', operation_time: '2026-04-18 14:20:00', operation_type: '配置变更', description: '修改可可豆注册奖励', before_value: '30', after_value: '50' },
  { id: '5', operator_id: 'admin02', operator_role: '管理员', operation_time: '2026-04-18 11:30:00', operation_type: '审核操作', description: '拒绝社区话题：话题ID#2048（违规内容）', before_value: '待审核', after_value: '已拒绝' },
];

interface LoginLog {
  id: string;
  login_time: string;
  admin_account: string;
  ip_address: string;
  ip_location: string;
  device_info: string;
  result: '成功' | '失败';
}

const MOCK_LOGIN_LOGS: LoginLog[] = [
  { id: '1', login_time: '2026-04-19 10:00:00', admin_account: 'superadmin', ip_address: '192.168.1.100', ip_location: '北京市', device_info: 'Chrome 120 / macOS', result: '成功' },
  { id: '2', login_time: '2026-04-19 09:50:00', admin_account: 'admin01', ip_address: '10.0.0.55', ip_location: '上海市', device_info: 'Firefox 118 / Windows', result: '成功' },
  { id: '3', login_time: '2026-04-19 09:45:00', admin_account: 'admin01', ip_address: '10.0.0.55', ip_location: '上海市', device_info: 'Firefox 118 / Windows', result: '失败' },
  { id: '4', login_time: '2026-04-18 17:30:00', admin_account: 'superadmin', ip_address: '192.168.1.100', ip_location: '北京市', device_info: 'Chrome 120 / macOS', result: '成功' },
];

export default function SecurityLogPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [filterType, setFilterType] = useState('');
  const [filterOperator, setFilterOperator] = useState('');
  const [filterDateStart, setFilterDateStart] = useState('');
  const [filterDateEnd, setFilterDateEnd] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => setLoading(false), 500);
    return () => clearTimeout(timer);
  }, [activeTab]);

  const handleExport = (format: string) => {
    alert(`导出${activeTab === 0 ? '操作日志' : '登录日志'}为 ${format.toUpperCase()} 格式（功能对接后端后实现）`);
  };

  if (loading) return <div className="loading-spinner">加载中...</div>;

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3 style={{ margin: 0 }}>安全日志与审计（§8.4）</h3>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-sm" onClick={() => handleExport('csv')}>导出CSV</button>
          <button className="btn btn-sm" onClick={() => handleExport('xlsx')}>导出Excel</button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 0, marginBottom: 16 }}>
        {LOG_TYPE_TABS.map((tab, idx) => (
          <button
            key={tab}
            className={`btn btn-sm ${activeTab === idx ? 'btn-primary' : ''}`}
            onClick={() => setActiveTab(idx)}
            style={{ borderRadius: idx === 0 ? '6px 0 0 6px' : '0 6px 6px 0' }}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="config-card">
        <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
          {activeTab === 0 && (
            <>
              <select
                className="config-input"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                style={{ width: 140 }}
              >
                <option value="">全部操作类型</option>
                {OPERATION_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
              <input
                className="config-input"
                type="text"
                placeholder="操作人账号"
                value={filterOperator}
                onChange={(e) => setFilterOperator(e.target.value)}
                style={{ width: 140 }}
              />
            </>
          )}
          <input
            className="config-input"
            type="date"
            value={filterDateStart}
            onChange={(e) => setFilterDateStart(e.target.value)}
          />
          <span style={{ lineHeight: '32px' }}>至</span>
          <input
            className="config-input"
            type="date"
            value={filterDateEnd}
            onChange={(e) => setFilterDateEnd(e.target.value)}
          />
          <button className="btn btn-primary btn-sm">筛选</button>
        </div>

        {activeTab === 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ boxShadow: 'none' }}>
              <thead>
                <tr>
                  <th>操作ID</th>
                  <th>操作人</th>
                  <th>角色</th>
                  <th>操作时间</th>
                  <th>操作类型</th>
                  <th>操作描述</th>
                  <th>变更前</th>
                  <th>变更后</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_OPERATION_LOGS.map((log) => (
                  <tr key={log.id}>
                    <td>{log.id}</td>
                    <td>{log.operator_id}</td>
                    <td><span className={`badge ${log.operator_role === '超级管理员' ? 'badge-error' : 'badge-info'}`}>{log.operator_role}</span></td>
                    <td>{log.operation_time}</td>
                    <td><span className="badge badge-default">{log.operation_type}</span></td>
                    <td style={{ maxWidth: 250 }}>{log.description}</td>
                    <td style={{ color: '#ff4d4f' }}>{log.before_value}</td>
                    <td style={{ color: '#52c41a' }}>{log.after_value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ boxShadow: 'none' }}>
              <thead>
                <tr>
                  <th>登录时间</th>
                  <th>管理员账号</th>
                  <th>IP地址</th>
                  <th>IP归属地</th>
                  <th>设备信息</th>
                  <th>登录结果</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_LOGIN_LOGS.map((log) => (
                  <tr key={log.id}>
                    <td>{log.login_time}</td>
                    <td>{log.admin_account}</td>
                    <td>{log.ip_address}</td>
                    <td>{log.ip_location}</td>
                    <td>{log.device_info}</td>
                    <td>
                      <span className={`badge ${log.result === '成功' ? 'badge-success' : 'badge-error'}`}>
                        {log.result}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div style={{ marginTop: 12, color: '#999', fontSize: 12 }}>
          日志不可删除、不可修改、不可关闭记录 | 保留周期：1年 | 支持按操作类型、操作人、时间范围组合筛选并导出
        </div>
      </div>
    </>
  );
}
