import { useState, useEffect } from 'react';
import { adminService } from '@/services/adminService';

export default function ConfigSecurityPage() {
  const [configs, setConfigs] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    adminService.getSystemConfigs()
      .then((res) => {
        const map: Record<string, string> = {};
        res.configs?.forEach((item) => { map[item.config_key] = item.config_value; });
        setConfigs(map);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const SECURITY_DEFAULTS: Record<string, string> = {
    security_ip_minute_limit: '100',
    security_ip_hour_limit: '2000',
    security_ua_blacklist: '',
    security_ban_duration_min: '30',
    security_log_retention_days: '90',
    security_beans_daily_user_limit: '1000',
    security_beans_daily_ip_limit: '10000',
    security_device_register_hour_limit: '5',
    security_ip_register_hour_limit: '20',
    security_beans_yellow_threshold: '80',
    security_beans_red_threshold: '100',
    content_api_secret: '',
    content_api_types: 'topic_content,reply_content',
    content_api_min_length: '50',
    content_api_high_risk_action: 'delete_notify',
    content_api_mid_risk_action: 'mark_pending',
    rate_limit_general_qps: '100',
    rate_limit_ai_qps: '50',
    rate_limit_download_qps: '200',
    rate_limit_register_qps: '20',
    rate_limit_db_pool: '100',
    rate_limit_redis_ttl: '300',
    rate_limit_sensitive_sync_min: '5',
    rate_limit_audit_lock_min: '15',
  };

  const handleReset = () => {
    setConfigs((p) => ({ ...p, ...SECURITY_DEFAULTS }));
    showToast('已恢复到默认值，请点击"保存配置"以生效', 'success');
  };

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const getVal = (key: string, def: string) => configs[key] ?? def;

  const renderField = (key: string, label: string, def: string, unit: string, min?: number, max?: number) => (
    <div className="config-row" key={key}>
      <div className="config-label">{label}</div>
      <div className="config-value">
        {editing ? (
          <>
            <input
              className="config-input"
              type="number"
              min={min}
              max={max}
              value={getVal(key, def)}
              onChange={(e) => setConfigs((p) => ({ ...p, [key]: e.target.value }))}
              style={{ width: 120 }}
            />
            <span className="config-unit">{unit}</span>
            {min !== undefined && <span style={{ color: '#999', fontSize: 11, marginLeft: 4 }}>({min}~{max})</span>}
          </>
        ) : (
          <>
            <span style={{ fontWeight: 500 }}>{getVal(key, def)}</span>
            <span className="config-unit">{unit}</span>
          </>
        )}
      </div>
    </div>
  );

  const handleSave = async (keys: string[]) => {
    setSaving(true);
    try {
      for (const key of keys) {
        if (configs[key] !== undefined) await adminService.updateSystemConfig(key, configs[key]);
      }
      showToast('配置已保存', 'success');
      setEditing(false);
    } catch {
      showToast('保存失败', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="loading-spinner">加载中...</div>;

  const TABS = ['反爬虫配置', '反刷可可豆', '内容安全API', '限流配置'];

  const allKeys = [
    'security_ip_minute_limit', 'security_ip_hour_limit', 'security_ua_blacklist',
    'security_ban_duration_min', 'security_log_retention_days',
    'security_beans_daily_user_limit', 'security_beans_daily_ip_limit',
    'security_device_register_hour_limit', 'security_ip_register_hour_limit',
    'security_beans_yellow_threshold', 'security_beans_red_threshold',
    'content_api_secret', 'content_api_types', 'content_api_min_length',
    'content_api_high_risk_action', 'content_api_mid_risk_action',
    'rate_limit_general_qps', 'rate_limit_ai_qps', 'rate_limit_download_qps', 'rate_limit_register_qps',
    'rate_limit_db_pool', 'rate_limit_redis_ttl', 'rate_limit_sensitive_sync_min', 'rate_limit_audit_lock_min',
  ];

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
        <div className="config-card">
          <div className="config-card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>反爬虫与反恶意爬取（§8.1 M5-F042）</span>
            {editing && (
              <button className="btn btn-primary btn-sm" disabled={saving} onClick={() => handleSave([
                'security_ip_minute_limit', 'security_ip_hour_limit', 'security_ban_duration_min', 'security_log_retention_days',
              ])}>
                {saving ? '保存中...' : '保存配置'}
              </button>
            )}
          </div>
          {renderField('security_ip_minute_limit', '单IP每分钟请求上限', '100', '次', 10, 10000)}
          {renderField('security_ip_hour_limit', '单IP每小时请求上限', '2000', '次', 100, 100000)}
          <div className="config-row">
            <div className="config-label">UA黑名单</div>
            <div className="config-value">
              {editing ? (
                <textarea
                  value={getVal('security_ua_blacklist', '')}
                  onChange={(e) => setConfigs((p) => ({ ...p, security_ua_blacklist: e.target.value }))}
                  style={{ width: '100%', padding: 8, border: '1px solid #d9d9d9', borderRadius: 6, minHeight: 60, fontSize: 13 }}
                  placeholder="每行一个User-Agent字符串或正则表达式"
                />
              ) : (
                <span style={{ color: getVal('security_ua_blacklist', '') ? '#333' : '#999' }}>
                  {getVal('security_ua_blacklist', '') || '未配置'}
                </span>
              )}
            </div>
          </div>
          {renderField('security_ban_duration_min', '自动封禁时长', '30', '分钟', 1, 1440)}
          <div className="config-row">
            <div className="config-label">触发处置动作</div>
            <div className="config-value">
              <div style={{ fontSize: 13, lineHeight: 1.8 }}>
                首次超限 → 返回429状态码+友好提示<br />
                连续3次超限 → 自动封禁IP {getVal('security_ban_duration_min', '30')}分钟
              </div>
            </div>
          </div>
          {renderField('security_log_retention_days', '日志保留周期', '90', '天', 7, 365)}
        </div>
      )}

      {activeTab === 1 && (
        <div className="config-card">
          <div className="config-card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>反可可豆刷取（§8.2 M5-F043）</span>
            {editing && (
              <button className="btn btn-primary btn-sm" disabled={saving} onClick={() => handleSave([
                'security_beans_daily_user_limit', 'security_beans_daily_ip_limit',
                'security_device_register_hour_limit', 'security_ip_register_hour_limit',
                'security_beans_yellow_threshold', 'security_beans_red_threshold',
              ])}>
                {saving ? '保存中...' : '保存配置'}
              </button>
            )}
          </div>
          <h4 style={{ margin: '0 0 8px', fontSize: 14, color: '#1890ff' }}>刷豆行为检测规则</h4>
          {renderField('security_beans_daily_user_limit', '单用户单日可可豆获取上限', '1000', '可可豆', 0, 999999)}
          {renderField('security_device_register_hour_limit', '同一设备注册次数上限（小时窗口）', '5', '次', 1, 100)}
          {renderField('security_ip_register_hour_limit', '同一IP注册次数上限（小时窗口）', '20', '次', 1, 1000)}
          {renderField('security_beans_daily_ip_limit', '同一IP每日可可豆获取上限', '10000', '可可豆', 0, 999999)}

          <h4 style={{ margin: '20px 0 8px', fontSize: 14, color: '#fa8c16' }}>异常交易监控</h4>
          {renderField('security_beans_yellow_threshold', '黄牌预警阈值（1小时获取占日上限%）', '80', '%', 50, 100)}
          {renderField('security_beans_red_threshold', '红牌预警阈值（1小时获取占日上限%）', '100', '%', 80, 100)}
          <div style={{ padding: '8px 12px', background: '#fff7e6', borderRadius: 6, fontSize: 13, color: '#ad6800', marginTop: 8 }}>
            🟡 黄牌预警：通知管理员关注 | 🔴 红牌预警：自动执行资产冻结（禁止消耗和转账，不影响登录浏览）
          </div>
        </div>
      )}

      {activeTab === 2 && (
        <div className="config-card">
          <div className="config-card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>微信内容安全API配置（§8.3 M5-F044）</span>
            {editing && (
              <button className="btn btn-primary btn-sm" disabled={saving} onClick={() => handleSave([
                'content_api_secret', 'content_api_types', 'content_api_min_length',
                'content_api_high_risk_action', 'content_api_mid_risk_action',
              ])}>
                {saving ? '保存中...' : '保存配置'}
              </button>
            )}
          </div>
          <div className="config-row">
            <div className="config-label">API Secret</div>
            <div className="config-value">
              {editing ? (
                <input
                  className="config-input"
                  type="password"
                  value={getVal('content_api_secret', '')}
                  onChange={(e) => setConfigs((p) => ({ ...p, content_api_secret: e.target.value }))}
                  style={{ width: 240 }}
                  placeholder="输入API Secret"
                />
              ) : (
                <span style={{ fontFamily: 'monospace' }}>{getVal('content_api_secret', '') ? '***' + getVal('content_api_secret', '').slice(-4) : '未配置'}</span>
              )}
              <span style={{ color: '#ff4d4f', fontSize: 12, marginLeft: 8 }}>加密存储，展示时脱敏</span>
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">内容类型开关</div>
            <div className="config-value">
              {editing ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {['话题标题', '话题内容', '回复内容', 'AI对话内容'].map((type) => (
                    <label key={type} style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                      <input type="checkbox" defaultChecked={type === '话题内容' || type === '回复内容'} />
                      <span style={{ fontSize: 13 }}>{type}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <span>话题内容 + 回复内容</span>
              )}
            </div>
          </div>
          {renderField('content_api_min_length', '调用内容长度门槛', '50', '字符', 10, 2000)}
          <div className="config-row">
            <div className="config-label">高风险回调处置</div>
            <div className="config-value">
              {editing ? (
                <select
                  className="config-input"
                  value={getVal('content_api_high_risk_action', 'delete_notify')}
                  onChange={(e) => setConfigs((p) => ({ ...p, content_api_high_risk_action: e.target.value }))}
                  style={{ width: 200 }}
                >
                  <option value="delete_notify">直接删除+通知用户</option>
                  <option value="mark_pending">仅标记待审</option>
                  <option value="silent_pass">静默放行（记录日志）</option>
                </select>
              ) : (
                <span>{getVal('content_api_high_risk_action', 'delete_notify') === 'delete_notify' ? '直接删除+通知用户' : getVal('content_api_high_risk_action', 'delete_notify') === 'mark_pending' ? '仅标记待审' : '静默放行'}</span>
              )}
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">中风险回调处置</div>
            <div className="config-value">
              {editing ? (
                <select
                  className="config-input"
                  value={getVal('content_api_mid_risk_action', 'mark_pending')}
                  onChange={(e) => setConfigs((p) => ({ ...p, content_api_mid_risk_action: e.target.value }))}
                  style={{ width: 200 }}
                >
                  <option value="mark_pending">标记待审</option>
                  <option value="silent_pass">静默放行（记录日志）</option>
                </select>
              ) : (
                <span>{getVal('content_api_mid_risk_action', 'mark_pending') === 'mark_pending' ? '标记待审' : '静默放行'}</span>
              )}
            </div>
          </div>
          <div style={{ padding: '8px 12px', background: '#f0f5ff', borderRadius: 6, fontSize: 13, color: '#1d39c4', marginTop: 8 }}>
            ℹ️ 微信内容安全API为基础内容审核兜底能力，核心审核仍以自建AI语义审核为主。API审核结果不直接作为最终处置依据，仅作为辅助参考。
          </div>
        </div>
      )}

      {activeTab === 3 && (
        <>
          <div className="config-card">
            <div className="config-card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>业务层限流（§8.5 M5-F046）</span>
              {editing && (
                <button className="btn btn-primary btn-sm" disabled={saving} onClick={() => handleSave([
                  'rate_limit_general_qps', 'rate_limit_ai_qps', 'rate_limit_download_qps', 'rate_limit_register_qps',
                ])}>
                  {saving ? '保存中...' : '保存配置'}
                </button>
              )}
            </div>
            {renderField('rate_limit_general_qps', '各接口QPS上限（通用）', '100', '次/秒', 1, 10000)}
            {renderField('rate_limit_ai_qps', 'AI对话接口QPS上限', '50', '次/秒', 1, 1000)}
            {renderField('rate_limit_download_qps', '资源下载接口QPS上限', '200', '次/秒', 1, 10000)}
            {renderField('rate_limit_register_qps', '注册接口QPS上限（防刷）', '20', '次/秒', 1, 1000)}
            <div style={{ padding: '8px 12px', background: '#f6ffed', borderRadius: 6, fontSize: 13, color: '#389e0d', marginTop: 8 }}>
              ℹ️ 限流规则修改后实时写入配置中心，各服务节点≤5秒内感知变更并生效，无需重启服务。
            </div>
          </div>

          <div className="config-card" style={{ marginTop: 16 }}>
            <div className="config-card-title">技术层限流（技术参考）</div>
            <div style={{ padding: '8px 12px', background: '#f5f5f5', borderRadius: 6, fontSize: 13, color: '#666', marginBottom: 12 }}>
              ⚙️ 以下参数为技术实现细节，由研发团队自行管理，不属于产品需求文档配置范畴。运营人员如需调整请联系研发团队。
            </div>
            {renderField('rate_limit_db_pool', '数据库连接池上限', '100', '个连接', 10, 500)}
            {renderField('rate_limit_redis_ttl', 'Redis缓存超时策略', '300', '秒', 0, 3600)}
            {renderField('rate_limit_sensitive_sync_min', '敏感词实时同步间隔', '5', '分钟', 1, 60)}
            {renderField('rate_limit_audit_lock_min', '审核领用锁定时长', '15', '分钟', 1, 60)}
          </div>
        </>
      )}

      <div style={{ marginTop: 16, textAlign: 'right' }}>
        {!editing ? (
          <button className="btn btn-primary btn-sm" onClick={() => setEditing(true)}>编辑配置</button>
        ) : (
          <>
            <button className="btn btn-sm" onClick={handleReset} disabled={saving}>恢复默认</button>
            <button className="btn btn-sm" onClick={() => setEditing(false)} disabled={saving}>取消编辑</button>
          </>
        )}
      </div>
    </>
  );
}
