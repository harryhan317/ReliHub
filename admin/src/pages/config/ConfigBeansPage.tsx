import { useState, useEffect } from 'react';
import { adminService } from '@/services/adminService';

export default function ConfigBeansPage() {
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
        if (configs[key] !== undefined) {
          await adminService.updateSystemConfig(key, configs[key]);
        }
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
          <div className="config-card-title">可可豆奖惩规则</div>
          <div className="config-row">
            <div className="config-label">注册奖励</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['beans_register_reward'] || '30'}
                onChange={(e) => setConfigs((p) => ({ ...p, beans_register_reward: e.target.value }))} />
              <span className="config-unit">🫘</span>
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">早鸟奖励</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['beans_early_bird_reward'] || '20'}
                onChange={(e) => setConfigs((p) => ({ ...p, beans_early_bird_reward: e.target.value }))} />
              <span className="config-unit">🫘</span>
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">每日签到</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['beans_daily_checkin'] || '2'}
                onChange={(e) => setConfigs((p) => ({ ...p, beans_daily_checkin: e.target.value }))} />
              <span className="config-unit">🫘/天</span>
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">邀请好友奖励</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['beans_invite_reward'] || '10'}
                onChange={(e) => setConfigs((p) => ({ ...p, beans_invite_reward: e.target.value }))} />
              <span className="config-unit">🫘/人</span>
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">资源被下载收益</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['beans_download_share'] || '70'}
                onChange={(e) => setConfigs((p) => ({ ...p, beans_download_share: e.target.value }))} />
              <span className="config-unit">% 归作者</span>
            </div>
          </div>
          <div className="config-row">
            <div className="config-label">通缩比例</div>
            <div className="config-value">
              <input className="config-input" type="number" value={configs['beans_deflation_rate'] || '30'}
                onChange={(e) => setConfigs((p) => ({ ...p, beans_deflation_rate: e.target.value }))} />
              <span className="config-unit">% 销毁</span>
            </div>
          </div>
          <div style={{ marginTop: 12 }}>
            <button className="btn btn-primary btn-sm" disabled={saving}
              onClick={() => handleSave(['beans_register_reward', 'beans_early_bird_reward', 'beans_daily_checkin', 'beans_invite_reward', 'beans_download_share', 'beans_deflation_rate'])}>
              保存配置
            </button>
          </div>
        </div>
        <div className="config-card">
          <div className="config-card-title">信誉分奖惩规则</div>
          <div className="config-row">
            <div className="config-label">每日签到</div>
            <div className="config-value">+1 <span className="config-unit">分/天</span></div>
          </div>
          <div className="config-row">
            <div className="config-label">资源被下载</div>
            <div className="config-value">+1 <span className="config-unit">分/次</span></div>
          </div>
          <div className="config-row">
            <div className="config-label">话题被采纳</div>
            <div className="config-value">+5 <span className="config-unit">分/次</span></div>
          </div>
          <div className="config-row">
            <div className="config-label">违规扣分</div>
            <div className="config-value">-5~-20 <span className="config-unit">分/次</span></div>
          </div>
          <div className="config-row">
            <div className="config-label">封号清零</div>
            <div className="config-value">归零 <span className="config-unit">分</span></div>
          </div>
          <div style={{ marginTop: 12 }}>
            <button className="btn btn-primary btn-sm">编辑规则</button>
          </div>
        </div>
      </div>
    </>
  );
}
