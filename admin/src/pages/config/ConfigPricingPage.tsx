import { useState, useEffect } from 'react';
import { adminService } from '@/services/adminService';

export default function ConfigPricingPage() {
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

  const PRICING_DEFAULTS: Record<string, string> = {
    pricing_admin_min: '5',
    pricing_admin_max: '100000',
    pricing_user_min: '5',
    pricing_user_max: '100000',
    pricing_warning_low_ratio: '0.5',
    pricing_warning_high_ratio: '2',
  };

  const handleReset = () => {
    setConfigs((p) => ({ ...p, ...PRICING_DEFAULTS }));
    showToast('已恢复到默认值，请点击"保存配置"以生效', 'success');
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
              style={{ width: 140 }}
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

  const handleSave = async () => {
    setSaving(true);
    try {
      const keys = [
        'pricing_admin_min', 'pricing_admin_max',
        'pricing_user_min', 'pricing_user_max',
        'pricing_warning_low_ratio', 'pricing_warning_high_ratio',
      ];
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

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}

      <div className="config-card">
        <div className="config-card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>资源定价区间配置</span>
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

        <div style={{ padding: '8px 12px', background: '#f0f5ff', borderRadius: 6, fontSize: 13, color: '#1d39c4', marginBottom: 16 }}>
          💡 超额提醒规则：当定价 &lt; 配置下限×0.5 或 定价 &gt; 配置上限×2 时，系统展示黄色警告提示（不阻断提交）
        </div>

        <h4 style={{ margin: '16px 0 8px', fontSize: 14, color: '#1890ff' }}>管理员资源定价区间</h4>
        {renderField('pricing_admin_min', '定价下限', '5', '可可豆', 0, 9999)}
        {renderField('pricing_admin_max', '定价上限', '100000', '可可豆', 0, 999999)}

        <h4 style={{ margin: '24px 0 8px', fontSize: 14, color: '#52c41a' }}>用户资源定价区间</h4>
        {renderField('pricing_user_min', '定价下限', '5', '可可豆', 0, 9999)}
        {renderField('pricing_user_max', '定价上限', '100000', '可可豆', 0, 999999)}

        <h4 style={{ margin: '24px 0 8px', fontSize: 14, color: '#fa8c16' }}>超额提醒系数</h4>
        {renderField('pricing_warning_low_ratio', '低价警告倍数', '0.5', '倍', 0, 1)}
        {renderField('pricing_warning_high_ratio', '高价警告倍数', '2', '倍', 1, 10)}
      </div>

      <div className="config-card" style={{ marginTop: 16 }}>
        <div className="config-card-title">基础资源标识</div>
        <div style={{ padding: '8px 12px', background: '#f6ffed', borderRadius: 6, fontSize: 13, color: '#389e0d', marginBottom: 12 }}>
          📌 管理员可在上传资源时通过勾选 is_seed=true 将资源标注为"基础资源"。基础资源仍须具备面值定价，在用户等级对应的权益额度内下载时，下载者不消耗可可豆。
        </div>
        <div className="config-row">
          <div className="config-label">批量标注权限</div>
          <div className="config-value">
            <span className="badge badge-info">仅限管理员上传资源或原作者已注销</span>
          </div>
        </div>
        <div className="config-row">
          <div className="config-label">强制转换通知</div>
          <div className="config-value">
            <span className="badge badge-success">已启用</span>
            <span style={{ color: '#999', fontSize: 12, marginLeft: 8 }}>强制转换正在收益中的资源时，自动向原作者发送站内通知</span>
          </div>
        </div>
        <div className="config-row">
          <div className="config-label">操作日志</div>
          <div className="config-value">
            <span className="badge badge-success">强制记录</span>
            <span style={{ color: '#999', fontSize: 12, marginLeft: 8 }}>每次批量标注操作均记录操作人/时间/被标注资源列表</span>
          </div>
        </div>
      </div>
    </>
  );
}
