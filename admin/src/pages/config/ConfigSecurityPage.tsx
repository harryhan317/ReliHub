import { useState, useEffect } from 'react';
import { adminService } from '@/services/adminService';

export default function ConfigSecurityPage() {
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

  const handleSave = async (keys: string[]) => {
    setSaving(true);
    try {
      for (const key of keys) {
        if (configs[key] !== undefined) await adminService.updateSystemConfig(key, configs[key]);
      }
      showToast('配置已保存', 'success');
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
      <div className="config-grid">
        <div className="config-card">
          <div className="config-card-title">反爬虫配置</div>
          <div className="config-row">
            <div className="config-label">单IP每分钟请求上限</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['security_ip_rate_limit'] || '60'}
                onChange={(e) => setConfigs((p) => ({ ...p, security_ip_rate_limit: e.target.value }))} />
              <span className="config-unit">次</span>
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">验证码触发阈值</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['security_captcha_threshold'] || '100'}
                onChange={(e) => setConfigs((p) => ({ ...p, security_captcha_threshold: e.target.value }))} />
              <span className="config-unit">次/小时</span>
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">自动封禁IP</div>
            <div className="config-value"><span className="badge badge-success">已启用</span></div>
          </div>
          <div style={{ marginTop: 12 }}>
            <button className="btn btn-primary btn-sm" disabled={saving}
              onClick={() => handleSave(['security_ip_rate_limit', 'security_captcha_threshold'])}>保存配置</button>
          </div>
        </div>
        <div className="config-card">
          <div className="config-card-title">反刷可可豆配置</div>
          <div className="config-row">
            <div className="config-label">每日签到上限</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['security_checkin_limit'] || '1'}
                onChange={(e) => setConfigs((p) => ({ ...p, security_checkin_limit: e.target.value }))} />
              <span className="config-unit">次/天</span>
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">邀请奖励上限</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['security_invite_limit'] || '10'}
                onChange={(e) => setConfigs((p) => ({ ...p, security_invite_limit: e.target.value }))} />
              <span className="config-unit">人/天</span>
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">异常行为检测</div>
            <div className="config-value"><span className="badge badge-success">已启用</span></div>
          </div>
          <div style={{ marginTop: 12 }}>
            <button className="btn btn-primary btn-sm" disabled={saving}
              onClick={() => handleSave(['security_checkin_limit', 'security_invite_limit'])}>保存配置</button>
          </div>
        </div>
        <div className="config-card">
          <div className="config-card-title">内容安全API配置</div>
          <div className="config-row">
            <div className="config-label">微信内容安全API</div>
            <div className="config-value"><span className="badge badge-success">已连接</span></div>
          </div>
          <div className="config-row">
            <div className="config-label">检测范围</div>
            <div className="config-value">资源/话题/回复/AI输出</div>
          </div>
          <div className="config-row">
            <div className="config-label">自动拦截</div>
            <div className="config-value"><span className="badge badge-success">已启用</span></div>
          </div>
          <div style={{ marginTop: 12 }}>
            <button className="btn btn-sm">测试连接</button>
          </div>
        </div>
        <div className="config-card">
          <div className="config-card-title">限流配置</div>
          <div className="config-row">
            <div className="config-label">AI对话限流</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['rate_limit_ai'] || '10'}
                onChange={(e) => setConfigs((p) => ({ ...p, rate_limit_ai: e.target.value }))} />
              <span className="config-unit">次/分钟</span>
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">资源下载限流</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['rate_limit_download'] || '5'}
                onChange={(e) => setConfigs((p) => ({ ...p, rate_limit_download: e.target.value }))} />
              <span className="config-unit">次/分钟</span>
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">社区发帖限流</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['rate_limit_community'] || '3'}
                onChange={(e) => setConfigs((p) => ({ ...p, rate_limit_community: e.target.value }))} />
              <span className="config-unit">次/分钟</span>
            </div>
          </div>
          <div style={{ marginTop: 12 }}>
            <button className="btn btn-primary btn-sm" disabled={saving}
              onClick={() => handleSave(['rate_limit_ai', 'rate_limit_download', 'rate_limit_community'])}>保存配置</button>
          </div>
        </div>
      </div>
    </>
  );
}
