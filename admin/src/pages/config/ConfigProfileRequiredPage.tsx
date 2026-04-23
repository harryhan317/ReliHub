import { useState, useEffect } from 'react';
import { adminService } from '@/services/adminService';

const LEVELS = ['新兵', '菜鸟', '入门', '熟手', '老炮', '达人', '专家'];
const LEVEL_KEYS = ['xinbing', 'cainiao', 'rumen', 'shushou', 'laopao', 'daren', 'zhuanjia'];

const FIELDS = [
  { key: 'nickname', label: '昵称' },
  { key: 'phone', label: '手机号' },
  { key: 'avatar', label: '头像' },
  { key: 'organization', label: '单位' },
  { key: 'position', label: '职务' },
  { key: 'bio', label: '个人简介' },
  { key: 'realname_auth', label: '实名认证' },
];

type FieldState = 'required' | 'optional' | 'hidden';

const DEFAULT_MATRIX: Record<string, FieldState[]> = {
  xinbing:   ['required', 'required', 'optional', 'optional', 'optional', 'optional', 'optional'],
  cainiao:   ['required', 'required', 'optional', 'optional', 'optional', 'optional', 'optional'],
  rumen:     ['required', 'required', 'optional', 'optional', 'optional', 'optional', 'optional'],
  shushou:   ['required', 'required', 'optional', 'optional', 'optional', 'optional', 'optional'],
  laopao:    ['required', 'required', 'optional', 'optional', 'optional', 'optional', 'optional'],
  daren:     ['required', 'required', 'optional', 'optional', 'optional', 'optional', 'required'],
  zhuanjia:  ['required', 'required', 'optional', 'optional', 'optional', 'optional', 'required'],
};

const STATE_LABELS: Record<FieldState, { label: string; color: string; bg: string }> = {
  required: { label: '必填', color: '#1890ff', bg: '#e6f7ff' },
  optional: { label: '选填', color: '#999', bg: '#f5f5f5' },
  hidden:   { label: '隐藏', color: '#ff4d4f', bg: '#fff1f0' },
};

export default function ConfigProfileRequiredPage() {
  const [configs, setConfigs] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const [matrix, setMatrix] = useState<Record<string, FieldState[]>>(() => {
    const m: Record<string, FieldState[]> = {};
    LEVEL_KEYS.forEach((key) => {
      m[key] = [...(DEFAULT_MATRIX[key] || FIELDS.map(() => 'optional' as FieldState))];
    });
    return m;
  });

  useEffect(() => {
    adminService.getSystemConfigs()
      .then((res) => {
        const map: Record<string, string> = {};
        res.configs?.forEach((item) => { map[item.config_key] = item.config_value; });
        setConfigs(map);
        if (map['profile_required_matrix']) {
          try {
            const parsed = JSON.parse(map['profile_required_matrix']) as Record<string, FieldState[]>;
            setMatrix(parsed);
          } catch { /* ignore */ }
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleReset = () => {
    const defaultMatrix: Record<string, FieldState[]> = {};
    LEVEL_KEYS.forEach((key) => {
      defaultMatrix[key] = [...(DEFAULT_MATRIX[key] || FIELDS.map(() => 'optional' as FieldState))];
    });
    setMatrix(defaultMatrix);
    showToast('已恢复到默认值，请点击"保存配置"以生效', 'success');
  };

  const cycleState = (levelKey: string, fieldIdx: number) => {
    setMatrix((prev) => {
      const row = [...(prev[levelKey] || [])];
      const current: FieldState = row[fieldIdx] || 'optional';
      const next: FieldState = current === 'required' ? 'optional' : current === 'optional' ? 'hidden' : 'required';
      row[fieldIdx] = next;
      return { ...prev, [levelKey]: row };
    });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await adminService.updateSystemConfig('profile_required_matrix', JSON.stringify(matrix));
      showToast('配置已保存', 'success');
      setEditing(false);
    } catch {
      showToast('保存失败', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="loading-spinner">加载中...</div>;

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}

      <div className="config-card">
        <div className="config-card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>个人信息等级必填项配置</span>
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

        <div style={{ padding: '8px 12px', background: '#fff7e6', borderRadius: 6, fontSize: 13, color: '#ad6800', marginBottom: 16 }}>
          ℹ️ 配置变更后，新注册用户立即适用新规则；存量用户不受影响，但在下次主动修改个人信息时需补齐新规则下的必填项。
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ boxShadow: 'none', minWidth: 700 }}>
            <thead>
              <tr>
                <th style={{ width: 80 }}>等级</th>
                {FIELDS.map((f) => (
                  <th key={f.key} style={{ textAlign: 'center', minWidth: 80 }}>{f.label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {LEVELS.map((level, i) => {
                const levelKey: string = LEVEL_KEYS[i] || '';
                return (
                  <tr key={levelKey}>
                    <td style={{ fontWeight: 500 }}>{level}</td>
                    {FIELDS.map((_, fi) => {
                      const state: FieldState = matrix[levelKey]?.[fi] || 'optional';
                      const info = STATE_LABELS[state];
                      return (
                        <td key={fi} style={{ textAlign: 'center' }}>
                          {editing ? (
                            <button
                              className="btn btn-sm"
                              onClick={() => cycleState(levelKey, fi)}
                              style={{
                                fontSize: 12,
                                padding: '2px 8px',
                                color: info.color,
                                background: info.bg,
                                border: `1px solid ${info.color}33`,
                                cursor: 'pointer',
                              }}
                            >
                              {info.label}
                            </button>
                          ) : (
                            <span style={{
                              fontSize: 12,
                              padding: '2px 8px',
                              color: info.color,
                              background: info.bg,
                              borderRadius: 4,
                              border: `1px solid ${info.color}33`,
                            }}>
                              {info.label}
                            </span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {editing && (
          <div style={{ marginTop: 12, color: '#999', fontSize: 12 }}>
            点击单元格可切换：必填 → 选填 → 隐藏 → 必填（循环切换）
          </div>
        )}
      </div>
    </>
  );
}
