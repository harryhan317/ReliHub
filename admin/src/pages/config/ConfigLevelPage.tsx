import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';

const LEVELS = [
  { key: 'xinbing', label: '新兵', badge: 'badge-info', min: 0, max: 99, upgrade: 100, warning: '-', demotion: '-' },
  { key: 'cainiao', label: '菜鸟', badge: 'badge-info', min: 100, max: 299, upgrade: 300, warning: '≤100', demotion: '<80' },
  { key: 'rumen', label: '入门', badge: 'badge-primary', min: 300, max: 599, upgrade: 600, warning: '≤300', demotion: '<240' },
  { key: 'shushou', label: '熟手', badge: 'badge-primary', min: 600, max: 999, upgrade: 1000, warning: '≤600', demotion: '<480' },
  { key: 'laopao', label: '老炮', badge: 'badge-success', min: 1000, max: 1999, upgrade: 2000, warning: '≤1000', demotion: '<800' },
  { key: 'daren', label: '达人', badge: 'badge-warning', min: 2000, max: null, upgrade: null, warning: '≤2000', demotion: '<1600' },
  { key: 'zhuanjia', label: '专家', badge: 'badge-error', min: 5000, max: null, upgrade: null, warning: '≤5000', demotion: '<4000' },
];

export default function ConfigLevelPage() {
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

  const LEVEL_DEFAULTS: Record<string, { min: number; max: number | null; upgrade: number | null }> = {
    xinbing: { min: 0, max: 99, upgrade: 100 },
    cainiao: { min: 100, max: 299, upgrade: 300 },
    rumen: { min: 300, max: 599, upgrade: 600 },
    shushou: { min: 600, max: 999, upgrade: 1000 },
    laopao: { min: 1000, max: 1999, upgrade: 2000 },
    daren: { min: 2000, max: null, upgrade: null },
    zhuanjia: { min: 5000, max: null, upgrade: null },
  };

  const handleReset = () => {
    const defaults: Record<string, string> = {};
    LEVELS.forEach((lv) => {
      const levelDefaults = LEVEL_DEFAULTS[lv.key];
      if (levelDefaults) {
        defaults[`level_${lv.key}_min`] = String(levelDefaults.min);
        if (levelDefaults.max !== null) {
          defaults[`level_${lv.key}_max`] = String(levelDefaults.max);
        }
      }
    });
    defaults['level_demotion_coefficient'] = '0.8';
    setConfigs((p) => ({ ...p, ...defaults }));
    showToast('已恢复到默认值，请点击"保存配置"以生效', 'success');
  };

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      const keys = Object.keys(configs).filter((k) => k.startsWith('level_'));
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

  const getLevelMin = (lv: typeof LEVELS[0]) => configs[`level_${lv.key}_min`] || String(lv.min);
  const getLevelMax = (lv: typeof LEVELS[0]) => {
    if (lv.max === null) return '无上限';
    return configs[`level_${lv.key}_max`] || String(lv.max);
  };
  const getDemotionThreshold = (lv: typeof LEVELS[0]) => {
    const min = parseInt(getLevelMin(lv));
    const coeff = parseFloat(configs['level_demotion_coefficient'] || '0.8');
    if (lv.key === 'xinbing') return '无（降无可降）';
    return `<${Math.floor(min * coeff)}`;
  };

  if (loading) return <div className="loading-spinner">加载中...</div>;

  const demotionCoeff = configs['level_demotion_coefficient'] || '0.8';

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}
      <div className="config-card">
        <div className="config-card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>等级体系与信誉分阈值配置（§5.2）</span>
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
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ boxShadow: 'none', minWidth: 800 }}>
            <thead>
              <tr>
                <th>等级名称</th>
                <th>信誉分下限(含)</th>
                <th>信誉分上限(不含)</th>
                <th>升级阈值</th>
                <th>预警触发</th>
                <th>降级阈值</th>
              </tr>
            </thead>
            <tbody>
              {LEVELS.map((lv) => (
                <tr key={lv.key}>
                  <td><span className={`badge ${lv.badge}`}>{lv.label}</span></td>
                  <td>
                    {editing ? (
                      <input
                        className="config-input"
                        type="number"
                        min={0}
                        max={10000}
                        value={getLevelMin(lv)}
                        onChange={(e) => setConfigs((p) => ({ ...p, [`level_${lv.key}_min`]: e.target.value }))}
                        style={{ width: 80 }}
                      />
                    ) : (
                      getLevelMin(lv)
                    )}
                  </td>
                  <td>
                    {lv.max === null ? '无上限' : (
                      editing ? (
                        <input
                          className="config-input"
                          type="number"
                          min={0}
                          max={10000}
                          value={configs[`level_${lv.key}_max`] || String(lv.max)}
                          onChange={(e) => setConfigs((p) => ({ ...p, [`level_${lv.key}_max`]: e.target.value }))}
                          style={{ width: 80 }}
                        />
                      ) : (
                        configs[`level_${lv.key}_max`] || String(lv.max)
                      )
                    )}
                  </td>
                  <td>{lv.upgrade !== null ? `≥${lv.upgrade}` : (lv.key === 'daren' ? '信誉分≥5000时提醒申请专家' : '需申请认证')}</td>
                  <td>{lv.warning}</td>
                  <td>{getDemotionThreshold(lv)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div style={{ marginTop: 16, padding: '12px 16px', background: '#f8f9fa', borderRadius: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontWeight: 500 }}>全局降级缓冲系数：</span>
            {editing ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <input
                  className="config-input"
                  type="number"
                  step="0.1"
                  min={0.5}
                  max={0.9}
                  value={demotionCoeff}
                  onChange={(e) => setConfigs((p) => ({ ...p, level_demotion_coefficient: e.target.value }))}
                  style={{ width: 80 }}
                />
                <span style={{ color: '#999', fontSize: 12 }}>可调范围 0.5~0.9</span>
              </div>
            ) : (
              <span style={{ fontWeight: 600, color: '#1890ff' }}>{demotionCoeff}</span>
            )}
            <span style={{ color: '#999', fontSize: 12 }}>
              降级阈值 = floor(等级下限 × {demotionCoeff}) = {Math.floor(100 * parseFloat(demotionCoeff))}（菜鸟示例）
            </span>
          </div>
        </div>
        <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
          升级规则：信誉分达到升级阈值时自动升级 | 降级规则：信誉分降至范围下限时预警，降至降级阈值时立即降级
        </div>
      </div>
    </>
  );
}
