import { useState, useEffect } from 'react';
import { adminService } from '@/services/adminService';

export default function ConfigAIPage() {
  const [configs, setConfigs] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
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

  const handleSave = async (key: string, value: string) => {
    setSaving(true);
    try {
      await adminService.updateSystemConfig(key, value);
      setConfigs((prev) => ({ ...prev, [key]: value }));
      showToast('配置已保存', 'success');
    } catch {
      showToast('保存失败', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="loading-spinner">加载中...</div>;

  const levelConfig = [
    { level: '游客', badge: 'badge-default', dailySessions: configs['ai_guest_daily_sessions'] || '3', maxRounds: configs['ai_guest_max_rounds'] || '3', priority: '低' },
    { level: '新兵', badge: 'badge-info', dailySessions: configs['ai_xinbing_daily_sessions'] || '10', maxRounds: configs['ai_xinbing_max_rounds'] || '10', priority: '中' },
    { level: '老兵', badge: 'badge-success', dailySessions: configs['ai_laobing_daily_sessions'] || '30', maxRounds: configs['ai_laobing_max_rounds'] || '20', priority: '高' },
    { level: '专家', badge: 'badge-warning', dailySessions: configs['ai_expert_daily_sessions'] || '无限', maxRounds: configs['ai_expert_max_rounds'] || '50', priority: '最高' },
  ];

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}
      <div className="config-grid">
        <div className="config-card">
          <div className="config-card-title">AI问答等级权益配置</div>
          <table className="data-table" style={{ boxShadow: 'none' }}>
            <thead>
              <tr>
                <th>等级</th>
                <th>每日对话次数</th>
                <th>单次最大轮次</th>
                <th>优先级</th>
              </tr>
            </thead>
            <tbody>
              {levelConfig.map((row) => (
                <tr key={row.level}>
                  <td><span className={`badge ${row.badge}`}>{row.level}</span></td>
                  <td>{row.dailySessions}次/天</td>
                  <td>{row.maxRounds}轮</td>
                  <td>{row.priority}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: 12 }}>
            <button className="btn btn-primary btn-sm" disabled={saving}>编辑配置</button>
          </div>
        </div>
        <div className="config-card">
          <div className="config-card-title">AI模型配置</div>
          <div className="config-row">
            <div className="config-label">当前模型</div>
            <div className="config-value">{configs['ai_model'] || 'GPT-4o-mini'}</div>
          </div>
          <div className="config-row">
            <div className="config-label">System Prompt版本</div>
            <div className="config-value">{configs['ai_prompt_version'] || 'v2.3'} <span className="badge badge-success">当前</span></div>
          </div>
          <div className="config-row">
            <div className="config-label">温度参数</div>
            <div className="config-value">
              <input
                className="config-input"
                type="number"
                step="0.1"
                value={configs['ai_temperature'] || '0.7'}
                onChange={(e) => setConfigs((p) => ({ ...p, ai_temperature: e.target.value }))}
              />
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">最大Token</div>
            <div className="config-value">
              <input
                className="config-input"
                type="number"
                value={configs['ai_max_tokens'] || '4096'}
                onChange={(e) => setConfigs((p) => ({ ...p, ai_max_tokens: e.target.value }))}
              />
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">RAG知识库</div>
            <div className="config-value"><span className="badge badge-warning">Phase 3</span></div>
          </div>
          <div style={{ marginTop: 12 }}>
            <button
              className="btn btn-primary btn-sm"
              disabled={saving}
              onClick={() => {
                if (configs['ai_temperature']) handleSave('ai_temperature', configs['ai_temperature']);
                if (configs['ai_max_tokens']) handleSave('ai_max_tokens', configs['ai_max_tokens']);
              }}
            >
              保存配置
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
