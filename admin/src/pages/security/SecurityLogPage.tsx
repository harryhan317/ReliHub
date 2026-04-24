import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';
import type { AuditLogItem, AuditLogListResponse } from '@/types';

const ACTION_TYPE_MAP: Record<string, string> = {
  'BAN_USER': '用户处置',
  'UNBAN_USER': '用户处置',
  'APPROVE_RESOURCE': '审核操作',
  'REJECT_RESOURCE': '审核操作',
  'APPROVE_TOPIC': '审核操作',
  'REJECT_TOPIC': '审核操作',
  'UPDATE_CONFIG': '配置变更',
  'CREATE_ADMIN': '管理员账号管理',
  'UPDATE_ADMIN': '管理员账号管理',
  'DELETE_ADMIN': '管理员账号管理',
  'ADMIN_LOGIN': '管理员登录',
  'ADMIN_LOGOUT': '管理员登出',
};

const REVERSE_ACTION_TYPE_MAP: Record<string, string> = Object.fromEntries(
  Object.entries(ACTION_TYPE_MAP).map(([k, v]) => [v, k])
);

const OPERATION_TYPES = ['全部操作类型', '配置变更', '审核操作', '用户处置', '管理员账号管理', '管理员登录', '管理员登出', '其他'];
const LOG_TYPE_TABS = ['操作日志', '登录日志'];

const CONFIG_KEY_NAMES: Record<string, string> = {
  'ai_beginner_max_tokens': 'AI新手-max_tokens',
  'ai_beginner_temperature': 'AI新手-temperature',
  'ai_beginner_top_p': 'AI新手-top_p',
  'ai_intermediate_max_tokens': 'AI中级-max_tokens',
  'ai_intermediate_temperature': 'AI中级-temperature',
  'ai_intermediate_top_p': 'AI中级-top_p',
  'ai_advanced_max_tokens': 'AI高级-max_tokens',
  'ai_advanced_temperature': 'AI高级-temperature',
  'ai_advanced_top_p': 'AI高级-top_p',
  'ai_expert_max_tokens': 'AI专家-max_tokens',
  'ai_expert_temperature': 'AI专家-temperature',
  'ai_expert_top_p': 'AI专家-top_p',
  'guest_daily_limit': '游客每日限制次数',
  'guest_max_file_size': '游客最大文件大小',
  'guest_max_file_count': '游客最大文件数量',
  'ai_response_timeout': 'AI响应超时时间',
  'ai_model_name': 'AI模型名称',
  'ai_base_url': 'AI服务地址',
  'ai_api_key': 'AI密钥',
};

export default function SecurityLogPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [filterType, setFilterType] = useState('');
  const [filterOperator, setFilterOperator] = useState('');
  const [filterDateStart, setFilterDateStart] = useState('');
  const [filterDateEnd, setFilterDateEnd] = useState('');
  const [loading, setLoading] = useState(false);
  const [operationLogs, setOperationLogs] = useState<AuditLogItem[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 20;
  const totalPages = Math.ceil(totalCount / pageSize);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const action = filterType && filterType !== '全部操作类型' ? REVERSE_ACTION_TYPE_MAP[filterType] : undefined;
      let filterAction = action;
      if (activeTab === 0) {
        filterAction = action;
      } else if (activeTab === 1) {
        filterAction = 'ADMIN_LOGIN,ADMIN_LOGOUT';
      }
      const res: AuditLogListResponse = await adminService.getAuditLogs({
        admin_id: filterOperator || undefined,
        action: filterAction,
        page: currentPage,
        page_size: pageSize
      });
      setOperationLogs(res.logs || []);
      setTotalCount(res.total || 0);
    } catch {
      setOperationLogs([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  }, [activeTab, filterType, filterOperator, currentPage]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const handleFilter = () => {
    setCurrentPage(1);
    fetchLogs();
  };

  const getConfigKeyName = (key: string): string => {
    return CONFIG_KEY_NAMES[key] || key;
  };

  const formatLogDetail = (log: AuditLogItem) => {
    try {
      if (log.action === 'UPDATE_CONFIG') {
        const before = log.before_data ? JSON.parse(log.before_data) : {};
        const after = log.after_data ? JSON.parse(log.after_data) : {};
        const keyName = getConfigKeyName(before.config_key || after.config_key || '');
        if (before.config_value !== undefined && after.config_value !== undefined) {
          return { key: keyName, before: before.config_value, after: after.config_value };
        }
        return { key: keyName, before: '-', after: after.config_value || '-' };
      }
      if (log.action === 'ADMIN_LOGIN' || log.action === 'ADMIN_LOGOUT') {
        const after = log.after_data ? JSON.parse(log.after_data) : {};
        return { key: '账号', before: '-', after: after.username || '-' };
      }
      const after = log.after_data ? JSON.parse(log.after_data) : {};
      return { key: '-', before: '-', after: after.detail || after.description || '-' };
    } catch {
      return { key: '-', before: '-', after: log.after_data || '-' };
    }
  };

  const handleExport = () => {
    if (operationLogs.length === 0) {
      alert('没有可导出的数据');
      return;
    }
    const headers = ['ID', '操作人', '操作类型', '配置项', '变更前', '变更后', 'IP地址', '时间'];
    const rows = operationLogs.map((log) => {
      const detail = formatLogDetail(log);
      return [
        log.id,
        log.admin_id,
        ACTION_TYPE_MAP[log.action] || log.action,
        detail.key,
        detail.before,
        detail.after,
        log.ip_address || '-',
        log.created_at,
      ];
    });
    const csv = [headers, ...rows].map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `操作日志_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderPageNumbers = () => {
    const pages: (number | string)[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (currentPage > 3) pages.push('...');
      for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
        pages.push(i);
      }
      if (currentPage < totalPages - 2) pages.push('...');
      pages.push(totalPages);
    }
    return pages;
  };

  if (loading && operationLogs.length === 0) return <div className="loading-spinner">加载中...</div>;

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3 style={{ margin: 0 }}>安全日志与审计</h3>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-sm" onClick={handleExport}>导出CSV</button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 0, marginBottom: 16 }}>
        {LOG_TYPE_TABS.map((tab, idx) => (
          <button
            key={tab}
            className={`btn btn-sm ${activeTab === idx ? 'btn-primary' : ''}`}
            onClick={() => { setActiveTab(idx); setCurrentPage(1); }}
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
          <button className="btn btn-primary btn-sm" onClick={handleFilter}>筛选</button>
        </div>

        {activeTab === 0 ? (
          <>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table" style={{ boxShadow: 'none' }}>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>操作人</th>
                    <th>操作类型</th>
                    <th>配置项</th>
                    <th>变更前</th>
                    <th>变更后</th>
                    <th>IP地址</th>
                    <th>操作时间</th>
                  </tr>
                </thead>
                <tbody>
                  {operationLogs.map((log) => {
                    const detail = formatLogDetail(log);
                    return (
                      <tr key={log.id}>
                        <td title={log.id}>{log.id.slice(0, 8)}</td>
                        <td>{log.admin_id.slice(0, 12)}</td>
                        <td><span className="badge badge-default">{ACTION_TYPE_MAP[log.action] || log.action}</span></td>
                        <td style={{ maxWidth: 150 }} title={detail.key}>{detail.key}</td>
                        <td style={{ maxWidth: 150 }} className={detail.before !== '-' && detail.before !== detail.after ? 'text-danger' : ''}>{detail.before}</td>
                        <td style={{ maxWidth: 150 }} className={detail.after !== '-' && detail.before !== detail.after ? 'text-success' : ''}>{detail.after}</td>
                        <td>{log.ip_address || '-'}</td>
                        <td style={{ whiteSpace: 'nowrap' }}>{log.created_at}</td>
                      </tr>
                    );
                  })}
                  {operationLogs.length === 0 && (
                    <tr><td colSpan={8} style={{ textAlign: 'center', padding: 32, color: '#999' }}>暂无数据</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            {totalCount > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 16 }}>
                <div style={{ color: '#666', fontSize: 13 }}>
                  共 {totalCount} 条记录，第 {currentPage}/{totalPages} 页
                </div>
                <div style={{ display: 'flex', gap: 4 }}>
                  <button
                    className="btn btn-sm"
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                  >
                    上一页
                  </button>
                  {renderPageNumbers().map((page, idx) => (
                    typeof page === 'number' ? (
                      <button
                        key={idx}
                        className={`btn btn-sm ${currentPage === page ? 'btn-primary' : ''}`}
                        onClick={() => setCurrentPage(page)}
                      >
                        {page}
                      </button>
                    ) : (
                      <span key={idx} style={{ padding: '0 8px', lineHeight: '32px' }}>{page}</span>
                    )
                  ))}
                  <button
                    className="btn btn-sm"
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                  >
                    下一页
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ boxShadow: 'none' }}>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>账号</th>
                  <th>操作类型</th>
                  <th>IP地址</th>
                  <th>登录时间</th>
                </tr>
              </thead>
              <tbody>
                {operationLogs.map((log) => (
                  <tr key={log.id}>
                    <td title={log.id}>{log.id.slice(0, 8)}</td>
                    <td>{log.admin_id.slice(0, 12)}</td>
                    <td><span className={`badge ${log.action === 'ADMIN_LOGIN' ? 'badge-success' : 'badge-warning'}`}>{log.action === 'ADMIN_LOGIN' ? '登录' : '登出'}</span></td>
                    <td>{log.ip_address || '-'}</td>
                    <td style={{ whiteSpace: 'nowrap' }}>{log.created_at}</td>
                  </tr>
                ))}
                {operationLogs.length === 0 && (
                  <tr><td colSpan={5} style={{ textAlign: 'center', padding: 32, color: '#999' }}>暂无登录记录</td></tr>
                )}
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
