import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';

const LEVELS = [
  { key: 'guest', label: '游客', badge: 'badge-default' },
  { key: 'xinbing', label: '新兵', badge: 'badge-info' },
  { key: 'cainiao', label: '菜鸟', badge: 'badge-info' },
  { key: 'rumen', label: '入门', badge: 'badge-primary' },
  { key: 'shushou', label: '熟手', badge: 'badge-primary' },
  { key: 'laopao', label: '老炮', badge: 'badge-success' },
  { key: 'daren', label: '达人', badge: 'badge-warning' },
  { key: 'zhuanjia', label: '专家', badge: 'badge-error' },
];

const DEFAULTS: Record<string, Record<string, string>> = {
  guest:   { daily_sessions: '3',  max_rounds: '10', daily_total_rounds: '15',  session_token_limit: '2' },
  xinbing: { daily_sessions: '5',  max_rounds: '10', daily_total_rounds: '30',  session_token_limit: '10' },
  cainiao: { daily_sessions: '5',  max_rounds: '15', daily_total_rounds: '40',  session_token_limit: '12' },
  rumen:   { daily_sessions: '8',  max_rounds: '15', daily_total_rounds: '50',  session_token_limit: '16' },
  shushou: { daily_sessions: '10', max_rounds: '15', daily_total_rounds: '80',  session_token_limit: '16' },
  laopao:  { daily_sessions: '12', max_rounds: '20', daily_total_rounds: '100', session_token_limit: '24' },
  daren:   { daily_sessions: '15', max_rounds: '20', daily_total_rounds: '120', session_token_limit: '32' },
  zhuanjia:{ daily_sessions: '20', max_rounds: '20', daily_total_rounds: '150', session_token_limit: '32' },
};

const PARAM_LABELS: Record<string, string> = {
  daily_sessions: '每日新会话上限(个/天)',
  max_rounds: '单会话轮次上限(轮次)',
  daily_total_rounds: '每日问答总轮次上限(轮次/天)',
  session_token_limit: '单会话Token上限(K)',
};

const PARAM_RANGES: Record<string, { min: number; max: number; unit: string }> = {
  daily_sessions: { min: 1, max: 999, unit: '次/天' },
  max_rounds: { min: 1, max: 100, unit: '轮' },
  daily_total_rounds: { min: 1, max: 999, unit: '轮/天' },
  session_token_limit: { min: 1, max: 1024, unit: 'K' },
};

type LevelConfig = Record<string, string>;

export default function ConfigAIPage() {
  const [configs, setConfigs] = useState<Record<string, LevelConfig>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    adminService.getSystemConfigs()
      .then((res) => {
        const map: Record<string, string> = {};
        res.configs?.forEach((item) => { map[item.config_key] = item.config_value; });
        const parsed: Record<string, LevelConfig> = {};
        LEVELS.forEach((lv) => {
          const levelConfig: LevelConfig = {};
          Object.keys(DEFAULTS[lv.key] || {}).forEach((param) => {
            const cfgKey = `ai_${lv.key}_${param}`;
            levelConfig[param] = map[cfgKey] || (DEFAULTS[lv.key] || {})[param] || '';
          });
          parsed[lv.key] = levelConfig;
        });
        setConfigs(parsed);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleReset = () => {
    const defaultConfigs: Record<string, LevelConfig> = {};
    LEVELS.forEach((lv) => {
      defaultConfigs[lv.key] = { ...DEFAULTS[lv.key] };
    });
    setConfigs(defaultConfigs);
    showToast('已恢复到默认值，请点击"保存配置"以生效', 'success');
  };

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      const updates: Promise<unknown>[] = [];
      LEVELS.forEach((lv) => {
        Object.keys(DEFAULTS[lv.key] || {}).forEach((param) => {
          const cfgKey = `ai_${lv.key}_${param}`;
          const value = configs[lv.key]?.[param];
          if (value !== undefined) {
            updates.push(adminService.updateSystemConfig(cfgKey, value));
          }
        });
      });
      await Promise.all(updates);
      showToast('配置已保存，预计10秒内生效', 'success');
      setEditing(false);
    } catch {
      showToast('保存失败', 'error');
    } finally {
      setSaving(false);
    }
  }, [configs, showToast]);

  const updateConfig = (levelKey: string, param: string, value: string) => {
    setConfigs((prev) => ({
      ...prev,
      [levelKey]: { ...prev[levelKey], [param]: value },
    }));
  };

  if (loading) return <div className="loading-spinner">加载中...</div>;

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}
      <div className="config-card">
        <div className="config-card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>AI问答等级权益配置（§5.1）</span>
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
          <table className="data-table" style={{ boxShadow: 'none', minWidth: 900 }}>
            <thead>
              <tr>
                <th style={{ minWidth: 80 }}>等级</th>
                {Object.keys(PARAM_LABELS).map((param) => (
                  <th key={param} style={{ minWidth: 160 }}>{PARAM_LABELS[param]}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {LEVELS.map((lv) => (
                <tr key={lv.key}>
                  <td><span className={`badge ${lv.badge}`}>{lv.label}</span></td>
                  {Object.keys(PARAM_LABELS).map((param) => {
                    const range = PARAM_RANGES[param] || { min: 0, max: 999, unit: '' };
                    const value = configs[lv.key]?.[param] || (DEFAULTS[lv.key] || {})[param] || '';
                    return (
                      <td key={param}>
                        {editing ? (
                          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                            <input
                              className="config-input"
                              type="number"
                              min={range.min}
                              max={range.max}
                              value={value}
                              onChange={(e) => updateConfig(lv.key, param, e.target.value)}
                              style={{ width: 80 }}
                            />
                            <span style={{ color: '#999', fontSize: 12 }}>{range.unit}</span>
                          </div>
                        ) : (
                          <span>{value} {range.unit}</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
          可调范围：每日新会话1~999次 | 单会话轮次1~100轮 | 每日总轮次1~999轮 | 单会话Token 1~1024K
        </div>
      </div>
    </>
  );
}
