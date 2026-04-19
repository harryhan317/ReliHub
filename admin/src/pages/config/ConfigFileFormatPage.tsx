import { useState, useEffect } from 'react';
import { adminService } from '@/services/adminService';

const DOC_FORMATS = ['txt', 'doc', 'docx', 'pdf', 'xls', 'xlsx', 'ppt', 'pptx'];
const IMG_FORMATS = ['PNG', 'JPG', 'JPEG', 'BMP', 'TIF', 'GIF'];

export default function ConfigFileFormatPage() {
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

  const getVal = (key: string, def: string) => configs[key] ?? def;

  const getDocFormats = () => {
    const val = getVal('file_doc_formats', DOC_FORMATS.join(','));
    return val.split(',').map((s) => s.trim().toLowerCase());
  };

  const getImgFormats = () => {
    const val = getVal('file_img_formats', 'PNG,JPG,JPEG');
    return val.split(',').map((s) => s.trim().toUpperCase());
  };

  const toggleDocFormat = (fmt: string) => {
    const current = getDocFormats();
    const next = current.includes(fmt) ? current.filter((f) => f !== fmt) : [...current, fmt];
    setConfigs((p) => ({ ...p, file_doc_formats: next.join(',') }));
  };

  const toggleImgFormat = (fmt: string) => {
    const current = getImgFormats();
    const next = current.includes(fmt) ? current.filter((f) => f !== fmt) : [...current, fmt];
    setConfigs((p) => ({ ...p, file_img_formats: next.join(',') }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const keys = [
        'file_doc_formats', 'file_img_formats',
        'file_doc_max_size_mb', 'file_img_max_size_mb',
        'file_session_storage_mb', 'file_session_attach_limit',
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
          <span>文件格式与上传限制配置（§5.7 M5-F018）</span>
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

        <div className="config-row">
          <div className="config-label">文档类支持格式</div>
          <div className="config-value">
            {editing ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                <button className="btn btn-sm" onClick={() => setConfigs((p) => ({ ...p, file_doc_formats: DOC_FORMATS.join(',') }))}>全选</button>
                <button className="btn btn-sm" onClick={() => setConfigs((p) => ({ ...p, file_doc_formats: '' }))}>取消全选</button>
                {DOC_FORMATS.map((fmt) => (
                  <label key={fmt} style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={getDocFormats().includes(fmt)}
                      onChange={() => toggleDocFormat(fmt)}
                    />
                    <span style={{ fontSize: 13 }}>.{fmt}</span>
                  </label>
                ))}
              </div>
            ) : (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {getDocFormats().map((fmt) => (
                  <span key={fmt} className="badge badge-info">.{fmt}</span>
                ))}
                {getDocFormats().length === 0 && <span style={{ color: '#999' }}>未配置</span>}
              </div>
            )}
          </div>
        </div>

        <div className="config-row">
          <div className="config-label">图片类支持格式</div>
          <div className="config-value">
            {editing ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                <button className="btn btn-sm" onClick={() => setConfigs((p) => ({ ...p, file_img_formats: IMG_FORMATS.join(',') }))}>全选</button>
                <button className="btn btn-sm" onClick={() => setConfigs((p) => ({ ...p, file_img_formats: '' }))}>取消全选</button>
                {IMG_FORMATS.map((fmt) => (
                  <label key={fmt} style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={getImgFormats().includes(fmt)}
                      onChange={() => toggleImgFormat(fmt)}
                    />
                    <span style={{ fontSize: 13 }}>.{fmt}</span>
                  </label>
                ))}
              </div>
            ) : (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {getImgFormats().map((fmt) => (
                  <span key={fmt} className="badge badge-info">.{fmt}</span>
                ))}
                {getImgFormats().length === 0 && <span style={{ color: '#999' }}>未配置</span>}
              </div>
            )}
          </div>
        </div>

        <div className="config-row">
          <div className="config-label">文档类单文件最大容量</div>
          <div className="config-value">
            {editing ? (
              <>
                <input
                  className="config-input"
                  type="number"
                  min={1}
                  max={1024}
                  value={getVal('file_doc_max_size_mb', '20')}
                  onChange={(e) => setConfigs((p) => ({ ...p, file_doc_max_size_mb: e.target.value }))}
                  style={{ width: 100 }}
                />
                <span className="config-unit">MB（1~1024）</span>
              </>
            ) : (
              <>
                <span style={{ fontWeight: 500 }}>{getVal('file_doc_max_size_mb', '20')}</span>
                <span className="config-unit">MB</span>
              </>
            )}
          </div>
        </div>

        <div className="config-row">
          <div className="config-label">图片类单文件最大容量</div>
          <div className="config-value">
            {editing ? (
              <>
                <input
                  className="config-input"
                  type="number"
                  min={1}
                  max={100}
                  value={getVal('file_img_max_size_mb', '5')}
                  onChange={(e) => setConfigs((p) => ({ ...p, file_img_max_size_mb: e.target.value }))}
                  style={{ width: 100 }}
                />
                <span className="config-unit">MB（1~100）</span>
              </>
            ) : (
              <>
                <span style={{ fontWeight: 500 }}>{getVal('file_img_max_size_mb', '5')}</span>
                <span className="config-unit">MB</span>
              </>
            )}
          </div>
        </div>

        <div className="config-row">
          <div className="config-label">用户历史会话总保存空间</div>
          <div className="config-value">
            {editing ? (
              <>
                <input
                  className="config-input"
                  type="number"
                  min={1}
                  max={10240}
                  value={getVal('file_session_storage_mb', '100')}
                  onChange={(e) => setConfigs((p) => ({ ...p, file_session_storage_mb: e.target.value }))}
                  style={{ width: 100 }}
                />
                <span className="config-unit">MB（1~10240）</span>
              </>
            ) : (
              <>
                <span style={{ fontWeight: 500 }}>{getVal('file_session_storage_mb', '100')}</span>
                <span className="config-unit">MB</span>
              </>
            )}
          </div>
        </div>

        <div className="config-row">
          <div className="config-label">单会话附件上传个数上限</div>
          <div className="config-value">
            {editing ? (
              <>
                <input
                  className="config-input"
                  type="number"
                  min={0}
                  max={100}
                  value={getVal('file_session_attach_limit', '10')}
                  onChange={(e) => setConfigs((p) => ({ ...p, file_session_attach_limit: e.target.value }))}
                  style={{ width: 100 }}
                />
                <span className="config-unit">个（0~100）</span>
              </>
            ) : (
              <>
                <span style={{ fontWeight: 500 }}>{getVal('file_session_attach_limit', '10')}</span>
                <span className="config-unit">个</span>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
