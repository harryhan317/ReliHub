import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';

interface ConfigRow {
  key: string;
  label: string;
  defaultValue: string;
  min?: number;
  max?: number;
  unit: string;
}

const BEANS_REWARD: ConfigRow[] = [
  { key: 'beans_register_reward', label: '注册奖励', defaultValue: '30', min: 0, max: 100, unit: '可可豆' },
  { key: 'beans_early_bird_quota', label: '早鸟名额上限', defaultValue: '200', min: 0, max: 1000, unit: '人' },
  { key: 'beans_early_bird_reward', label: '早鸟奖励值', defaultValue: '20', min: 0, max: 100, unit: '可可豆' },
  { key: 'beans_daily_checkin', label: '每日签到奖励', defaultValue: '2', min: 0, max: 100, unit: '可可豆/天' },
  { key: 'beans_upload_reward', label: '资源上传（通过审核）', defaultValue: '30', min: 0, max: 100, unit: '可可豆' },
  { key: 'beans_first_category_reward', label: '首次分类额外奖励', defaultValue: '30', min: 0, max: 100, unit: '可可豆' },
  { key: 'beans_topic_reward', label: '发起话题（通过审核）', defaultValue: '10', min: 0, max: 50, unit: '可可豆' },
  { key: 'beans_first_topic_category_reward', label: '首次话题分类额外奖励', defaultValue: '10', min: 0, max: 50, unit: '可可豆' },
  { key: 'beans_invite_reward', label: '邀请奖励（邀请人）', defaultValue: '10', min: 0, max: 100, unit: '可可豆' },
  { key: 'beans_invited_reward', label: '邀请奖励（被邀请人）', defaultValue: '10', min: 0, max: 100, unit: '可可豆' },
  { key: 'beans_download_share', label: '资源被下载贡献者收益比例', defaultValue: '70', min: 60, max: 70, unit: '%' },
  { key: 'beans_topic_adopted_reward', label: '话题被采纳奖励', defaultValue: '20', min: 5, max: 200, unit: '可可豆' },
  { key: 'beans_reply_adopted_reward', label: '回复被采纳奖励', defaultValue: '10', min: 1, max: 100, unit: '可可豆' },
];

const CREDIT_REWARD: ConfigRow[] = [
  { key: 'credit_register_reward', label: '完成注册', defaultValue: '50', unit: '分' },
  { key: 'credit_daily_checkin', label: '每日签到', defaultValue: '1', min: 1, max: 5, unit: '分/天' },
  { key: 'credit_upload_reward', label: '资源上传（通过审核）', defaultValue: '20', min: 10, max: 50, unit: '分' },
  { key: 'credit_download_reward', label: '资源被下载', defaultValue: '2', min: 1, max: 10, unit: '分/次' },
  { key: 'credit_favorite_reward', label: '资源被收藏', defaultValue: '3', min: 1, max: 10, unit: '分/次' },
  { key: 'credit_like_reward', label: '被点赞', defaultValue: '1', min: 1, max: 5, unit: '分/次' },
  { key: 'credit_reply_reward', label: '回复话题', defaultValue: '5', min: 3, max: 20, unit: '分/次' },
  { key: 'credit_topic_reward', label: '发起话题（通过审核）', defaultValue: '10', min: 5, max: 30, unit: '分' },
  { key: 'credit_adopted_reward', label: '被采纳奖励', defaultValue: '30', min: 20, max: 100, unit: '分' },
];

const CREDIT_PENALTY: ConfigRow[] = [
  { key: 'credit_violation_speech', label: '违规发言（被举报核实）', defaultValue: '-20', min: -100, max: -10, unit: '分' },
  { key: 'credit_cheat_penalty', label: '恶意刷分（系统判定）', defaultValue: '-50', min: -200, max: -30, unit: '分' },
  { key: 'credit_duplicate_upload', label: '恶意重复上传资源', defaultValue: '-10', min: -50, max: -5, unit: '分' },
  { key: 'credit_malicious_report', label: '恶意举报', defaultValue: '-15', min: -50, max: -10, unit: '分' },
  { key: 'credit_spam_content', label: '发布垃圾内容', defaultValue: '-10', min: -50, max: -5, unit: '分' },
  { key: 'credit_confirmed_violation', label: '被举报确认违规', defaultValue: '-30', min: -100, max: -20, unit: '分' },
  { key: 'credit_inactive_penalty', label: '长期不登录', defaultValue: '-5', min: -20, max: -3, unit: '分/月' },
];

export default function ConfigBeansPage() {
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

  const BEANS_DEFAULTS: Record<string, string> = {
    beans_register_reward: '30',
    beans_early_bird_quota: '200',
    beans_early_bird_reward: '20',
    beans_daily_checkin: '2',
    beans_upload_reward: '30',
    beans_first_category_reward: '30',
    beans_topic_reward: '10',
    beans_first_topic_category_reward: '10',
    beans_invite_reward: '10',
    beans_invited_reward: '10',
    beans_download_share: '70',
    beans_topic_adopted_reward: '20',
    beans_reply_adopted_reward: '10',
    beans_deflation_rate: '30',
    beans_early_bird_enabled: 'true',
  };

  const CREDIT_REWARD_DEFAULTS: Record<string, string> = {
    credit_register_reward: '50',
    credit_daily_checkin: '1',
    credit_upload_reward: '20',
    credit_download_reward: '2',
    credit_favorite_reward: '3',
    credit_like_reward: '1',
    credit_reply_reward: '5',
    credit_topic_reward: '10',
    credit_adopted_reward: '30',
    credit_invite_reward: '10',
  };

  const CREDIT_PENALTY_DEFAULTS: Record<string, string> = {
    credit_violation_speech: '-20',
    credit_cheat_penalty: '-50',
    credit_duplicate_upload: '-10',
    credit_malicious_report: '-15',
    credit_spam_content: '-10',
    credit_confirmed_violation: '-30',
    credit_inactive_penalty: '-5',
    credit_duplicate_threshold: '80',
  };

  const handleReset = () => {
    const defaults = { ...BEANS_DEFAULTS, ...CREDIT_REWARD_DEFAULTS, ...CREDIT_PENALTY_DEFAULTS };
    setConfigs((p) => ({ ...p, ...defaults }));
    showToast('已恢复到默认值，请点击"保存配置"以生效', 'success');
  };

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      const allKeys = [
        ...BEANS_REWARD, ...CREDIT_REWARD, ...CREDIT_PENALTY,
      ].map((r) => r.key);
      allKeys.push('beans_deflation_rate', 'beans_early_bird_enabled', 'credit_duplicate_threshold');
      for (const key of allKeys) {
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

  const renderRow = (row: ConfigRow) => (
    <div className="config-row" key={row.key}>
      <div className="config-label">{row.label}</div>
      <div className="config-value">
        {editing ? (
          <>
            <input
              className="config-input"
              type="number"
              min={row.min}
              max={row.max}
              value={getVal(row.key, row.defaultValue)}
              onChange={(e) => setConfigs((p) => ({ ...p, [row.key]: e.target.value }))}
            />
            <span className="config-unit">{row.unit}</span>
            {row.min !== undefined && <span style={{ color: '#999', fontSize: 11, marginLeft: 4 }}>({row.min}~{row.max})</span>}
          </>
        ) : (
          <>
            <span style={{ fontWeight: 500 }}>{getVal(row.key, row.defaultValue)}</span>
            <span className="config-unit">{row.unit}</span>
          </>
        )}
      </div>
    </div>
  );

  if (loading) return <div className="loading-spinner">加载中...</div>;

  const downloadShare = parseInt(getVal('beans_download_share', '70'));
  const deflationRate = 100 - downloadShare;
  const earlyBirdEnabled = getVal('beans_early_bird_enabled', 'true') === 'true';

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3 style={{ margin: 0 }}>可可豆与信誉分奖惩规则配置（§5.4）</h3>
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
        <div className="config-card-title">可可豆获取规则（§5.4.1）</div>
        {BEANS_REWARD.map(renderRow)}
        <div className="config-row" style={{ background: '#f6ffed', borderRadius: 6, padding: '8px 12px' }}>
          <div className="config-label" style={{ fontWeight: 600 }}>贡献者收益 ↔ 通缩销毁联动</div>
          <div className="config-value">
            {editing ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span>贡献者</span>
                <input
                  className="config-input"
                  type="number"
                  min={60}
                  max={70}
                  value={getVal('beans_download_share', '70')}
                  onChange={(e) => {
                    const v = parseInt(e.target.value);
                    if (v >= 60 && v <= 70) {
                      setConfigs((p) => ({ ...p, beans_download_share: e.target.value, beans_deflation_rate: String(100 - v) }));
                    }
                  }}
                  style={{ width: 60 }}
                />
                <span>%</span>
                <span style={{ margin: '0 8px' }}>↔</span>
                <span>平台销毁</span>
                <span style={{ fontWeight: 600, color: '#ff4d4f' }}>{100 - downloadShare}%</span>
                <span style={{ color: '#999', fontSize: 12 }}>(自动计算)</span>
              </div>
            ) : (
              <span>贡献者 {downloadShare}% ↔ 平台销毁 <span style={{ fontWeight: 600, color: '#ff4d4f' }}>{deflationRate}%</span></span>
            )}
          </div>
        </div>
        <div className="config-row" style={{ background: '#f0f5ff', borderRadius: 6, padding: '8px 12px' }}>
          <div className="config-label" style={{ fontWeight: 600 }}>通缩比例配置（§5.4.4）</div>
          <div className="config-value">
            {editing ? (
              <>
                <input
                  className="config-input"
                  type="number"
                  min={20}
                  max={40}
                  value={getVal('beans_deflation_rate', '30')}
                  onChange={(e) => setConfigs((p) => ({ ...p, beans_deflation_rate: e.target.value }))}
                  style={{ width: 60 }}
                />
                <span className="config-unit">% 销毁</span>
                <span style={{ color: '#999', fontSize: 11, marginLeft: 4 }}>(可调20%~40%)</span>
              </>
            ) : (
              <>
                <span style={{ fontWeight: 500 }}>{getVal('beans_deflation_rate', '30')}</span>
                <span className="config-unit">% 销毁</span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="config-card" style={{ marginTop: 16 }}>
        <div className="config-card-title">早鸟活动配置（§5.4.5）</div>
        <div className="config-row">
          <div className="config-label">活动开关</div>
          <div className="config-value">
            {editing ? (
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={earlyBirdEnabled}
                  onChange={(e) => setConfigs((p) => ({ ...p, beans_early_bird_enabled: String(e.target.checked) }))}
                />
                <span>{earlyBirdEnabled ? '已开启' : '已关闭'}</span>
              </label>
            ) : (
              <span className={`badge ${earlyBirdEnabled ? 'badge-success' : 'badge-default'}`}>
                {earlyBirdEnabled ? '已开启' : '已关闭'}
              </span>
            )}
          </div>
        </div>
        {BEANS_REWARD[1] && renderRow(BEANS_REWARD[1])}
        {BEANS_REWARD[2] && renderRow(BEANS_REWARD[2])}
      </div>

      <div className="config-card" style={{ marginTop: 16 }}>
        <div className="config-card-title">邀请活动配置（§5.4.6）</div>
        {BEANS_REWARD[8] && renderRow(BEANS_REWARD[8])}
        {BEANS_REWARD[9] && renderRow(BEANS_REWARD[9])}
        <div className="config-row">
          <div className="config-label">邀请人奖励信誉分</div>
          <div className="config-value">
            {editing ? (
              <>
                <input
                  className="config-input"
                  type="number"
                  min={0}
                  max={100}
                  value={getVal('credit_invite_reward', '10')}
                  onChange={(e) => setConfigs((p) => ({ ...p, credit_invite_reward: e.target.value }))}
                />
                <span className="config-unit">分</span>
              </>
            ) : (
              <>
                <span style={{ fontWeight: 500 }}>{getVal('credit_invite_reward', '10')}</span>
                <span className="config-unit">分</span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="config-card" style={{ marginTop: 16 }}>
        <div className="config-card-title">信誉分增加规则（§5.4.3）</div>
        {CREDIT_REWARD.map(renderRow)}
      </div>

      <div className="config-card" style={{ marginTop: 16 }}>
        <div className="config-card-title">信誉分减少规则（§5.4.3）</div>
        {CREDIT_PENALTY.map(renderRow)}
        <div className="config-row" style={{ background: '#fff7e6', borderRadius: 6, padding: '8px 12px' }}>
          <div className="config-label">重复上传相似度阈值</div>
          <div className="config-value">
            {editing ? (
              <>
                <input
                  className="config-input"
                  type="number"
                  min={50}
                  max={100}
                  value={getVal('credit_duplicate_threshold', '80')}
                  onChange={(e) => setConfigs((p) => ({ ...p, credit_duplicate_threshold: e.target.value }))}
                  style={{ width: 60 }}
                />
                <span className="config-unit">%</span>
                <span style={{ color: '#999', fontSize: 11, marginLeft: 4 }}>(AI预审相似度阈值)</span>
              </>
            ) : (
              <>
                <span style={{ fontWeight: 500 }}>{getVal('credit_duplicate_threshold', '80')}</span>
                <span className="config-unit">%</span>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
