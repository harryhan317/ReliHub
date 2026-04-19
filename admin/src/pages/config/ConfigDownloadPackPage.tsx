import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';

export default function ConfigDownloadPackPage() {
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

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      const keys = [
        'pack_discount_price', 'pack_discount_capacity', 'pack_discount_rate',
        'pack_premium_price', 'pack_premium_capacity', 'pack_premium_rate',
        'pack_capacity_stackable',
      ];
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

  const getVal = (key: string, defaultVal: string) => configs[key] || defaultVal;

  const renderField = (key: string, label: string, defaultVal: string, unit: string, min?: number, max?: number) => (
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
              step={key.includes('rate') ? '0.01' : undefined}
              value={getVal(key, defaultVal)}
              onChange={(e) => setConfigs((p) => ({ ...p, [key]: e.target.value }))}
              style={{ width: 100 }}
            />
            <span className="config-unit">{unit}</span>
            {min !== undefined && <span style={{ color: '#999', fontSize: 11, marginLeft: 4 }}>({min}~{max})</span>}
          </>
        ) : (
          <>
            <span style={{ fontWeight: 500 }}>{getVal(key, defaultVal)}</span>
            <span className="config-unit">{unit}</span>
          </>
        )}
      </div>
    </div>
  );

  if (loading) return <div className="loading-spinner">加载中...</div>;

  const discountRate = parseFloat(getVal('pack_discount_rate', '0.85'));
  const premiumRate = parseFloat(getVal('pack_premium_rate', '0.70'));
  const stackable = getVal('pack_capacity_stackable', 'false') === 'true';

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3 style={{ margin: 0 }}>下载扩充包定价配置（§5.11）</h3>
        <div style={{ display: 'flex', gap: 8 }}>
          {editing ? (
            <>
              <button className="btn btn-sm" onClick={() => setEditing(false)} disabled={saving}>取消</button>
              <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>
                {saving ? '保存中...' : '保存配置'}
              </button>
            </>
          ) : (
            <button className="btn btn-primary btn-sm" onClick={() => setEditing(true)}>编辑配置</button>
          )}
        </div>
      </div>

      <div className="config-grid">
        <div className="config-card">
          <div className="config-card-title">特惠包配置</div>
          {renderField('pack_discount_price', '价格', '80', '可可豆', 1, 10000)}
          {renderField('pack_discount_capacity', '容量', '100', 'MB', 1, 10000)}
          {renderField('pack_discount_rate', '折扣率', '0.85', `(${Math.round(discountRate * 100)}%)`, 0.50, 1.00)}
          <div style={{ marginTop: 8, padding: '8px 12px', background: '#f6ffed', borderRadius: 6, fontSize: 13 }}>
            实付比例：{Math.round(discountRate * 100)}% | 贡献者收益：70% | 平台销毁：{Math.round(discountRate * 100) - 70}%
          </div>
        </div>

        <div className="config-card">
          <div className="config-card-title">畅享包配置</div>
          {renderField('pack_premium_price', '价格', '350', '可可豆', 1, 100000)}
          {renderField('pack_premium_capacity', '容量', '500', 'MB', 1, 100000)}
          {renderField('pack_premium_rate', '折扣率', '0.70', `(${Math.round(premiumRate * 100)}%)`, 0.50, 1.00)}
          <div style={{ marginTop: 8, padding: '8px 12px', background: '#f6ffed', borderRadius: 6, fontSize: 13 }}>
            实付比例：{Math.round(premiumRate * 100)}% | 贡献者收益：70% | 平台销毁：{Math.round(premiumRate * 100) - 70}%
          </div>
        </div>
      </div>

      <div className="config-card" style={{ marginTop: 16 }}>
        <div className="config-card-title">通用规则</div>
        <div className="config-row">
          <div className="config-label">有效期</div>
          <div className="config-value">
            <span className="badge badge-success">永久有效</span>
            <span style={{ color: '#999', fontSize: 12, marginLeft: 8 }}>MVP阶段不支持设置到期日</span>
          </div>
        </div>
        <div className="config-row">
          <div className="config-label">旧包剩余容量叠加</div>
          <div className="config-value">
            {editing ? (
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={stackable}
                  onChange={(e) => setConfigs((p) => ({ ...p, pack_capacity_stackable: String(e.target.checked) }))}
                />
                <span>{stackable ? '允许叠加' : '不可叠加（默认）'}</span>
              </label>
            ) : (
              <span className={`badge ${stackable ? 'badge-success' : 'badge-default'}`}>
                {stackable ? '允许叠加' : '不可叠加（默认）'}
              </span>
            )}
          </div>
        </div>
        <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
          消费扣减优先级：优先消耗每日免费权益额度/次数，免费额度耗尽后自动扣减已购买的扩充包
        </div>
      </div>
    </>
  );
}
