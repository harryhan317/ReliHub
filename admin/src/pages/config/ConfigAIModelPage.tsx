import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';

const PROVIDERS = ['OpenAI', 'Azure OpenAI', 'Claude (Anthropic)', 'DeepSeek', '自定义'];

interface PromptVersion {
  id: string;
  version: string;
  content: string;
  operator: string;
  publishTime: string;
  isActive: boolean;
}

const MOCK_PROMPT_VERSIONS: PromptVersion[] = [
  { id: '1', version: 'v2.3', content: '你是ReliHub的AI助手，专注于可靠性工程领域...', operator: 'superadmin', publishTime: '2026-04-15 10:30:00', isActive: true },
  { id: '2', version: 'v2.2', content: '你是ReliHub的AI助手，专注于可靠性工程领域...', operator: 'superadmin', publishTime: '2026-04-10 14:20:00', isActive: false },
  { id: '3', version: 'v2.1', content: '你是ReliHub的AI助手...', operator: 'superadmin', publishTime: '2026-04-05 09:15:00', isActive: false },
];

export default function ConfigAIModelPage() {
  const [configs, setConfigs] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);
  const [promptVersions] = useState<PromptVersion[]>(MOCK_PROMPT_VERSIONS);
  const [showPromptEditor, setShowPromptEditor] = useState(false);
  const [promptContent, setPromptContent] = useState('');
  const [showTestPanel, setShowTestPanel] = useState(false);
  const [testQuestion, setTestQuestion] = useState('');
  const [testAnswer, setTestAnswer] = useState('');
  const [testLoading, setTestLoading] = useState(false);

  useEffect(() => {
    adminService.getSystemConfigs()
      .then((res) => {
        const map: Record<string, string> = {};
        res.configs?.forEach((item) => { map[item.config_key] = item.config_value; });
        setConfigs(map);
        setPromptContent(map['ai_system_prompt'] || '你是ReliHub的AI助手，专注于可靠性工程领域，帮助用户解答可靠性、维修性、测试性等相关问题。');
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const AI_MODEL_DEFAULTS: Record<string, string> = {
    ai_provider: 'DeepSeek',
    ai_base_url: 'https://api.deepseek.com',
    ai_api_key: '',
    ai_model_version: 'deepseek-chat',
    ai_price_input: '1',
    ai_price_output: '2',
    ai_timeout: '30',
    ai_temperature: '0.7',
    ai_system_prompt: '你是ReliHub的AI助手，专注于可靠性工程领域，帮助用户解答可靠性、维修性、测试性等相关问题。',
  };

  const handleReset = () => {
    setConfigs((prev) => ({ ...prev, ...AI_MODEL_DEFAULTS }));
    setPromptContent(AI_MODEL_DEFAULTS.ai_system_prompt);
    showToast('已恢复到默认值，请点击"保存配置"以生效', 'success');
  };

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      const keys = ['ai_provider', 'ai_base_url', 'ai_api_key', 'ai_model_version',
        'ai_price_input', 'ai_price_output', 'ai_timeout', 'ai_temperature',
        'ai_system_prompt'];
      for (const key of keys) {
        if (configs[key] !== undefined) {
          await adminService.updateSystemConfig(key, configs[key] as string);
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

  const maskApiKey = (key: string) => {
    if (!key || key.length < 8) return '***';
    return '***' + key.slice(-4);
  };

  const handleTestPrompt = () => {
    if (!testQuestion.trim()) return;
    setTestLoading(true);
    setTestAnswer('');
    setTimeout(() => {
      setTestAnswer(`[模拟回复] 基于当前System Prompt配置，AI将对"${testQuestion}"的回答如下：\n\n这是使用当前Prompt版本生成的模拟回复，实际效果需对接真实AI服务后验证。`);
      setTestLoading(false);
    }, 1500);
  };

  if (loading) return <div className="loading-spinner">加载中...</div>;

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3 style={{ margin: 0 }}>AI模型与系统提示词配置（§5.5）</h3>
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

      <div className="config-card">
        <div className="config-card-title">AI大模型基础配置（§5.5）</div>
        <div className="config-row">
          <div className="config-label">API服务商</div>
          <div className="config-value">
            {editing ? (
              <select
                className="config-input"
                value={getVal('ai_provider', 'DeepSeek')}
                onChange={(e) => setConfigs((p) => ({ ...p, ai_provider: e.target.value }))}
                style={{ width: 180 }}
              >
                {PROVIDERS.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            ) : (
              <span style={{ fontWeight: 500 }}>{getVal('ai_provider', 'DeepSeek')}</span>
            )}
          </div>
        </div>
        <div className="config-row">
          <div className="config-label">API地址（Base URL）</div>
          <div className="config-value">
            {editing ? (
              <input
                className="config-input"
                type="url"
                value={getVal('ai_base_url', 'https://api.deepseek.com')}
                onChange={(e) => setConfigs((p) => ({ ...p, ai_base_url: e.target.value }))}
                style={{ width: 300 }}
              />
            ) : (
              <span style={{ fontWeight: 500 }}>{getVal('ai_base_url', 'https://api.deepseek.com')}</span>
            )}
          </div>
        </div>
        <div className="config-row">
          <div className="config-label">API密钥</div>
          <div className="config-value">
            {editing ? (
              <input
                className="config-input"
                type="password"
                value={getVal('ai_api_key', '')}
                onChange={(e) => setConfigs((p) => ({ ...p, ai_api_key: e.target.value }))}
                placeholder="输入API密钥（加密存储）"
                style={{ width: 300 }}
              />
            ) : (
              <span style={{ fontWeight: 500, color: '#999' }}>{maskApiKey(getVal('ai_api_key', ''))}</span>
            )}
            {!editing && <span style={{ color: '#999', fontSize: 11, marginLeft: 8 }}>展示时脱敏</span>}
          </div>
        </div>
        <div className="config-row">
          <div className="config-label">模型版本</div>
          <div className="config-value">
            {editing ? (
              <input
                className="config-input"
                type="text"
                value={getVal('ai_model_version', 'deepseek-chat')}
                onChange={(e) => setConfigs((p) => ({ ...p, ai_model_version: e.target.value }))}
                style={{ width: 200 }}
              />
            ) : (
              <span style={{ fontWeight: 500 }}>{getVal('ai_model_version', 'deepseek-chat')}</span>
            )}
          </div>
        </div>
        <div className="config-row">
          <div className="config-label">单价（输入）</div>
          <div className="config-value">
            {editing ? (
              <>
                <input
                  className="config-input"
                  type="number"
                  step="0.0001"
                  min={0}
                  max={999.9999}
                  value={getVal('ai_price_input', '1')}
                  onChange={(e) => setConfigs((p) => ({ ...p, ai_price_input: e.target.value }))}
                  style={{ width: 100 }}
                />
                <span className="config-unit">元/1M Token</span>
              </>
            ) : (
              <>
                <span style={{ fontWeight: 500 }}>{getVal('ai_price_input', '1')}</span>
                <span className="config-unit">元/1M Token</span>
              </>
            )}
          </div>
        </div>
        <div className="config-row">
          <div className="config-label">单价（输出）</div>
          <div className="config-value">
            {editing ? (
              <>
                <input
                  className="config-input"
                  type="number"
                  step="0.0001"
                  min={0}
                  max={999.9999}
                  value={getVal('ai_price_output', '2')}
                  onChange={(e) => setConfigs((p) => ({ ...p, ai_price_output: e.target.value }))}
                  style={{ width: 100 }}
                />
                <span className="config-unit">元/1M Token</span>
              </>
            ) : (
              <>
                <span style={{ fontWeight: 500 }}>{getVal('ai_price_output', '2')}</span>
                <span className="config-unit">元/1M Token</span>
              </>
            )}
          </div>
        </div>
        <div className="config-row">
          <div className="config-label">超时时间</div>
          <div className="config-value">
            {editing ? (
              <>
                <input
                  className="config-input"
                  type="number"
                  min={1}
                  max={120}
                  value={getVal('ai_timeout', '30')}
                  onChange={(e) => setConfigs((p) => ({ ...p, ai_timeout: e.target.value }))}
                  style={{ width: 80 }}
                />
                <span className="config-unit">秒</span>
              </>
            ) : (
              <>
                <span style={{ fontWeight: 500 }}>{getVal('ai_timeout', '30')}</span>
                <span className="config-unit">秒</span>
              </>
            )}
          </div>
        </div>
        <div className="config-row">
          <div className="config-label">温度参数</div>
          <div className="config-value">
            {editing ? (
              <>
                <input
                  className="config-input"
                  type="number"
                  step="0.1"
                  min={0}
                  max={2}
                  value={getVal('ai_temperature', '0.7')}
                  onChange={(e) => setConfigs((p) => ({ ...p, ai_temperature: e.target.value }))}
                  style={{ width: 80 }}
                />
                <span className="config-unit">(0~2)</span>
              </>
            ) : (
              <>
                <span style={{ fontWeight: 500 }}>{getVal('ai_temperature', '0.7')}</span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="config-card" style={{ marginTop: 16 }}>
        <div className="config-card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>System Prompt配置（§5.5.1）</span>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-sm" onClick={() => setShowTestPanel(!showTestPanel)}>
              {showTestPanel ? '关闭测试' : '预览测试'}
            </button>
            <button className="btn btn-primary btn-sm" onClick={() => setShowPromptEditor(true)}>编辑Prompt</button>
          </div>
        </div>
        <div style={{ marginTop: 8, padding: '12px 16px', background: '#f8f9fa', borderRadius: 8, fontSize: 13 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <span>当前激活版本：<strong>{promptVersions.find((v) => v.isActive)?.version || 'v2.3'}</strong></span>
            <span>最大8192字符 | 当前 {promptContent.length} 字符</span>
          </div>
          <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, color: '#333', maxHeight: 120, overflow: 'auto' }}>
            {promptContent}
          </div>
        </div>

        {showTestPanel && (
          <div style={{ marginTop: 12, padding: 16, border: '1px solid #d9d9d9', borderRadius: 8 }}>
            <div style={{ fontWeight: 500, marginBottom: 8 }}>Prompt预览测试</div>
            <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
              <input
                className="config-input"
                type="text"
                value={testQuestion}
                onChange={(e) => setTestQuestion(e.target.value)}
                placeholder="输入测试问题..."
                style={{ flex: 1 }}
              />
              <button className="btn btn-primary btn-sm" onClick={handleTestPrompt} disabled={testLoading}>
                {testLoading ? '测试中...' : '发送测试'}
              </button>
            </div>
            {testAnswer && (
              <div style={{ padding: 12, background: '#f0f5ff', borderRadius: 6, whiteSpace: 'pre-wrap', fontSize: 13 }}>
                {testAnswer}
              </div>
            )}
          </div>
        )}

        <div style={{ marginTop: 16 }}>
          <div style={{ fontWeight: 500, marginBottom: 8 }}>历史版本管理</div>
          <table className="data-table" style={{ boxShadow: 'none' }}>
            <thead>
              <tr>
                <th>版本号</th>
                <th>操作人</th>
                <th>发布时间</th>
                <th>内容摘要</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {promptVersions.map((v) => (
                <tr key={v.id}>
                  <td>{v.version}</td>
                  <td>{v.operator}</td>
                  <td>{v.publishTime}</td>
                  <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {v.content.slice(0, 40)}...
                  </td>
                  <td>
                    {v.isActive ? <span className="badge badge-success">当前激活</span> : <span className="badge badge-default">历史</span>}
                  </td>
                  <td>
                    {!v.isActive && (
                      <button className="btn btn-sm" onClick={() => {
                        setPromptContent(v.content);
                        setConfigs((p) => ({ ...p, ai_system_prompt: v.content }));
                        showToast(`已回滚至${v.version}，请保存配置以生效`, 'success');
                      }}>
                        回滚
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
          变更后仅对操作时刻之后新建的会话生效，已开启的历史会话继续沿用创建时的Prompt快照
        </div>
      </div>

      <div className="config-card" style={{ marginTop: 16 }}>
        <div className="config-card-title">RAG知识库管理（§5.5.2）</div>
        <div style={{ padding: '20px 16px', textAlign: 'center', color: '#999' }}>
          <span className="badge badge-warning">Phase 3</span>
          <span style={{ marginLeft: 8 }}>RAG知识库功能将在Phase 3上线，当前仅预埋表结构</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ boxShadow: 'none' }}>
            <thead>
              <tr>
                <th>参数</th>
                <th>默认值</th>
                <th>可调范围</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: '文档切片大小', defaultVal: '500字符', range: '100~2000字符' },
                { name: '切片重叠量', defaultVal: '50字符', range: '0~200字符' },
                { name: '向量检索召回数量(Top-K)', defaultVal: '5', range: '1~20' },
                { name: '相关性阈值', defaultVal: '0.7', range: '0.1~1.0' },
              ].map((row) => (
                <tr key={row.name}>
                  <td>{row.name}</td>
                  <td>{row.defaultVal}</td>
                  <td>{row.range}</td>
                  <td><span className="badge badge-warning">Phase 3</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showPromptEditor && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', borderRadius: 12, padding: 24, width: 700, maxHeight: '80vh', overflow: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ margin: 0 }}>编辑System Prompt</h3>
              <button className="btn btn-sm" onClick={() => setShowPromptEditor(false)}>关闭</button>
            </div>
            <div style={{ marginBottom: 8, color: '#999', fontSize: 12 }}>
              最大8192字符 | 当前 {promptContent.length} 字符 | 仅超级管理员可编辑
            </div>
            <textarea
              value={promptContent}
              onChange={(e) => {
                if (e.target.value.length <= 8192) {
                  setPromptContent(e.target.value);
                  setConfigs((p) => ({ ...p, ai_system_prompt: e.target.value }));
                }
              }}
              style={{ width: '100%', minHeight: 300, padding: 12, border: '1px solid #d9d9d9', borderRadius: 8, fontSize: 14, lineHeight: 1.6, resize: 'vertical' }}
            />
            <div style={{ marginTop: 12, display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button className="btn btn-sm" onClick={() => setShowPromptEditor(false)}>取消</button>
              <button className="btn btn-primary btn-sm" onClick={() => {
                setShowPromptEditor(false);
                showToast('Prompt已更新，请保存配置以生效', 'success');
              }}>确认</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
