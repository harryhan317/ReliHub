import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';

const LEVELS = ['游客', '新兵', '菜鸟', '入门', '熟手', '老炮', '达人', '专家'];

const PERMISSIONS = [
  { key: 'resource_browse', label: '资源浏览', type: 'number', unit: '条/天', defaults: ['10', '无限', '无限', '无限', '无限', '无限', '无限', '无限'] },
  { key: 'resource_download', label: '基础资源下载次数', type: 'number', unit: '次', defaults: ['0', '3', '5', '8', '10', '15', '20', '30'] },
  { key: 'resource_upload', label: '资源上传', type: 'toggle', defaults: [false, true, true, true, true, true, true, true] },
  { key: 'community_browse', label: '社区浏览', type: 'number', unit: '条/天', defaults: ['10', '无限', '无限', '无限', '无限', '无限', '无限', '无限'] },
  { key: 'topic_create', label: '发起话题', type: 'toggle', defaults: [false, true, true, true, true, true, true, true] },
  { key: 'bounty_create', label: '发起悬赏', type: 'toggle', defaults: [false, true, true, true, true, true, true, true] },
  { key: 'expert_service', label: '提供专家咨询服务', type: 'toggle', defaults: [false, false, false, false, false, false, false, true] },
];

const ADMIN_PERMISSIONS = [
  { key: 'content_audit', label: '内容审核（资源/社区/举报）', admin: true, superAdmin: true },
  { key: 'user_view', label: '用户列表查看/详情查看', admin: true, superAdmin: true },
  { key: 'user_penalty', label: '用户违规处置', admin: false, superAdmin: true },
  { key: 'security_log', label: '安全日志查看', admin: true, superAdmin: true },
  { key: 'param_config', label: '参数配置（§5各节）', admin: false, superAdmin: true },
  { key: 'admin_management', label: '管理员账号管理', admin: false, superAdmin: true },
  { key: 'anti_crawl_config', label: '反爬/反刷规则配置', admin: false, superAdmin: true },
  { key: 'rate_limit_config', label: '限流配置', admin: false, superAdmin: true },
];

export default function ConfigPermissionPage() {
  const [configs, setConfigs] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
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

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const PERMISSION_DEFAULTS: Record<string, string> = {
    perm_resource_browse_0: '10', perm_resource_browse_1: '无限', perm_resource_browse_2: '无限',
    perm_resource_browse_3: '无限', perm_resource_browse_4: '无限', perm_resource_browse_5: '无限',
    perm_resource_browse_6: '无限', perm_resource_browse_7: '无限',
    perm_resource_download_0: '0', perm_resource_download_1: '3', perm_resource_download_2: '5',
    perm_resource_download_3: '8', perm_resource_download_4: '10', perm_resource_download_5: '15',
    perm_resource_download_6: '20', perm_resource_download_7: '30',
    perm_resource_upload_0: 'false', perm_resource_upload_1: 'true', perm_resource_upload_2: 'true',
    perm_resource_upload_3: 'true', perm_resource_upload_4: 'true', perm_resource_upload_5: 'true',
    perm_resource_upload_6: 'true', perm_resource_upload_7: 'true',
    perm_community_browse_0: '10', perm_community_browse_1: '无限', perm_community_browse_2: '无限',
    perm_community_browse_3: '无限', perm_community_browse_4: '无限', perm_community_browse_5: '无限',
    perm_community_browse_6: '无限', perm_community_browse_7: '无限',
    perm_topic_create_0: 'false', perm_topic_create_1: 'true', perm_topic_create_2: 'true',
    perm_topic_create_3: 'true', perm_topic_create_4: 'true', perm_topic_create_5: 'true',
    perm_topic_create_6: 'true', perm_topic_create_7: 'true',
    perm_bounty_create_0: 'false', perm_bounty_create_1: 'true', perm_bounty_create_2: 'true',
    perm_bounty_create_3: 'true', perm_bounty_create_4: 'true', perm_bounty_create_5: 'true',
    perm_bounty_create_6: 'true', perm_bounty_create_7: 'true',
    perm_expert_service_0: 'false', perm_expert_service_1: 'false', perm_expert_service_2: 'false',
    perm_expert_service_3: 'false', perm_expert_service_4: 'false', perm_expert_service_5: 'false',
    perm_expert_service_6: 'false', perm_expert_service_7: 'true',
  };

  const handleReset = () => {
    setConfigs((p) => ({ ...p, ...PERMISSION_DEFAULTS }));
    showToast('已恢复到默认值，请点击"保存配置"以生效', 'success');
  };

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      const keys = Object.keys(configs).filter((k) => k.startsWith('perm_'));
      for (const key of keys) {
        if (configs[key] !== undefined) {
          await adminService.updateSystemConfig(key, configs[key]);
        }
      }
      showToast('配置已保存', 'success');
      setEditing(false);
    } catch {
      showToast('保存失败', 'error');
    } finally {
      setSaving(false);
    }
  }, [configs, showToast]);

  const getValue = (permKey: string, levelIdx: number, defaults: string[] | boolean[]) => {
    const cfgKey = `perm_${permKey}_${levelIdx}`;
    if (configs[cfgKey] !== undefined) return configs[cfgKey];
    return String(defaults[levelIdx]);
  };

  const setValue = (permKey: string, levelIdx: number, value: string) => {
    setConfigs((p) => ({ ...p, [`perm_${permKey}_${levelIdx}`]: value }));
  };

  if (loading) return <div className="loading-spinner">加载中...</div>;

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}
      <div className="config-card">
        <div className="config-card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>功能权限配置（§5.3）</span>
          <div style={{ display: 'flex', gap: 8 }}>
            {editing ? (
              <>
                <button className="btn btn-sm" onClick={() => setEditing(false)} disabled={saving}>取消</button>
                <button className="btn btn-sm" onClick={handleReset} disabled={saving}>恢复默认</button>
                <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>
                  {saving ? '保存中...' : '保存配置'}
                </button>
              </>
            ) : (
              <button className="btn btn-primary btn-sm" onClick={() => setEditing(true)}>编辑配置</button>
            )}
          </div>
        </div>
        <div style={{ marginBottom: 16, padding: '8px 12px', background: '#fff7e6', borderRadius: 6, fontSize: 13, color: '#ad6800' }}>
          权益额度矩阵的唯一权威来源为 PRD_可可豆与信誉分体系 §4.1.2，此处仅执行可视化读写操作
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ boxShadow: 'none', minWidth: 1000 }}>
            <thead>
              <tr>
                <th style={{ minWidth: 140 }}>功能模块</th>
                {LEVELS.map((lv) => (
                  <th key={lv} style={{ minWidth: 80, textAlign: 'center' }}>{lv}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {PERMISSIONS.map((perm) => (
                <tr key={perm.key}>
                  <td>{perm.label}</td>
                  {LEVELS.map((_, idx) => {
                    const val = getValue(perm.key, idx, perm.defaults);
                    if (perm.type === 'toggle') {
                      const checked = val === 'true';
                      return (
                        <td key={idx} style={{ textAlign: 'center' }}>
                          {editing ? (
                            <input
                              type="checkbox"
                              checked={checked}
                              onChange={(e) => setValue(perm.key, idx, String(e.target.checked))}
                            />
                          ) : (
                            checked ? <span style={{ color: '#52c41a' }}>✓</span> : <span style={{ color: '#ff4d4f' }}>✗</span>
                          )}
                        </td>
                      );
                    }
                    return (
                      <td key={idx} style={{ textAlign: 'center' }}>
                        {editing ? (
                          <input
                            className="config-input"
                            type="text"
                            value={val}
                            onChange={(e) => setValue(perm.key, idx, e.target.value)}
                            style={{ width: 60, textAlign: 'center' }}
                          />
                        ) : (
                          <span>{val} {perm.unit}</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="config-card" style={{ marginTop: 16 }}>
        <div className="config-card-title">运营权限矩阵（管理员/超级管理员）</div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ boxShadow: 'none' }}>
            <thead>
              <tr>
                <th>功能</th>
                <th style={{ textAlign: 'center' }}>管理员</th>
                <th style={{ textAlign: 'center' }}>超级管理员</th>
              </tr>
            </thead>
            <tbody>
              {ADMIN_PERMISSIONS.map((perm) => (
                <tr key={perm.key}>
                  <td>{perm.label}</td>
                  <td style={{ textAlign: 'center' }}>
                    {perm.admin ? <span style={{ color: '#52c41a' }}>✅</span> : <span style={{ color: '#ff4d4f' }}>❌</span>}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    {perm.superAdmin ? <span style={{ color: '#52c41a' }}>✅</span> : <span style={{ color: '#ff4d4f' }}>❌</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
          管理员/超级管理员权限固定，不可自定义。S0级参数（AI问答/等级体系/功能权限/可可豆奖惩/AI模型）仅超级管理员可修改
        </div>
      </div>
    </>
  );
}
