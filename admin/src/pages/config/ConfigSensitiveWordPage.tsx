import { useState } from 'react';

interface SensitiveWord {
  id: string;
  word: string;
  category: 'blacklist' | 'risk';
  scope: string;
  createdAt: string;
  operator: string;
}

const MOCK_WORDS: SensitiveWord[] = [
  { id: '1', word: '赌博', category: 'blacklist', scope: '全部', createdAt: '2026-04-18 10:30', operator: 'super_admin' },
  { id: '2', word: '代开发票', category: 'blacklist', scope: '全部', createdAt: '2026-04-17 14:20', operator: 'super_admin' },
  { id: '3', word: '微[信信]公[众号汁]', category: 'risk', scope: '话题标题', createdAt: '2026-04-16 09:15', operator: 'super_admin' },
  { id: '4', word: '加微信', category: 'risk', scope: '话题内容', createdAt: '2026-04-15 16:40', operator: 'super_admin' },
  { id: '5', word: '刷单', category: 'blacklist', scope: '全部', createdAt: '2026-04-14 11:00', operator: 'super_admin' },
  { id: '6', word: '兼职.*日结', category: 'risk', scope: '回复内容', createdAt: '2026-04-13 08:30', operator: 'super_admin' },
  { id: '7', word: '色情', category: 'blacklist', scope: '全部', createdAt: '2026-04-12 15:20', operator: 'super_admin' },
  { id: '8', word: '贷款.*无抵押', category: 'risk', scope: '全部', createdAt: '2026-04-11 10:10', operator: 'super_admin' },
];

const SCOPES = ['全部', '话题标题', '话题内容', '回复内容'];

export default function ConfigSensitiveWordPage() {
  const [words, setWords] = useState<SensitiveWord[]>(MOCK_WORDS);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [searchText, setSearchText] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [newWord, setNewWord] = useState('');
  const [newCategory, setNewCategory] = useState<'blacklist' | 'risk'>('blacklist');
  const [newScope, setNewScope] = useState('全部');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleAdd = () => {
    if (!newWord.trim()) {
      showToast('请输入关键词', 'error');
      return;
    }
    const word: SensitiveWord = {
      id: String(Date.now()),
      word: newWord.trim(),
      category: newCategory,
      scope: newScope,
      createdAt: new Date().toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).replace(/\//g, '-'),
      operator: 'super_admin',
    };
    setWords((prev) => [word, ...prev]);
    setShowAddModal(false);
    setNewWord('');
    showToast('关键词已添加', 'success');
  };

  const handleBatchDelete = () => {
    if (selectedIds.size === 0) {
      showToast('请先选择要删除的关键词', 'error');
      return;
    }
    setWords((prev) => prev.filter((w) => !selectedIds.has(w.id)));
    setSelectedIds(new Set());
    setShowDeleteConfirm(false);
    showToast(`已删除${selectedIds.size}个关键词`, 'success');
  };

  const handleImport = () => {
    setShowImportModal(false);
    showToast('批量导入功能（对接后端API后实现）', 'success');
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === filteredWords.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredWords.map((w) => w.id)));
    }
  };

  const filteredWords = words.filter((w) => {
    if (categoryFilter && w.category !== categoryFilter) return false;
    if (searchText && !w.word.includes(searchText)) return false;
    return true;
  });

  return (
    <>
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}

      <div className="config-card">
        <div className="config-card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>敏感词库管理（§5.9 M5-F020）</span>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-sm" onClick={() => setShowImportModal(true)}>📥 批量导入</button>
            <button className="btn btn-primary btn-sm" onClick={() => setShowAddModal(true)}>➕ 新增关键词</button>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
          <div style={{ padding: '8px 12px', background: '#fff1f0', borderRadius: 6, fontSize: 13, color: '#cf1322', flex: 1, minWidth: 200 }}>
            🚫 黑名单关键词：命中后前端直接阻断提交，提示"包含敏感词，请修改后重试"
          </div>
          <div style={{ padding: '8px 12px', background: '#fff7e6', borderRadius: 6, fontSize: 13, color: '#ad6800', flex: 1, minWidth: 200 }}>
            ⚠️ 风控关键词：命中后允许提交，内容进入AI审核队列，由管理员决定是否放行
          </div>
        </div>

        <div className="toolbar" style={{ marginBottom: 12 }}>
          <div className="toolbar-left">
            <select className="filter-select" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
              <option value="">全部类别</option>
              <option value="blacklist">黑名单</option>
              <option value="risk">风控词</option>
            </select>
            <div className="search-box">
              <span>🔍</span>
              <input placeholder="搜索关键词" value={searchText} onChange={(e) => setSearchText(e.target.value)} />
            </div>
          </div>
          <div className="toolbar-right">
            {selectedIds.size > 0 && (
              <button className="btn btn-sm" style={{ color: '#ff4d4f' }} onClick={() => setShowDeleteConfirm(true)}>
                🗑️ 删除选中({selectedIds.size})
              </button>
            )}
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ boxShadow: 'none' }}>
            <thead>
              <tr>
                <th style={{ width: 40 }}>
                  <input type="checkbox" checked={selectedIds.size === filteredWords.length && filteredWords.length > 0} onChange={toggleSelectAll} />
                </th>
                <th>关键词</th>
                <th>类别</th>
                <th>生效范围</th>
                <th>添加时间</th>
                <th>操作人</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredWords.map((w) => (
                <tr key={w.id}>
                  <td><input type="checkbox" checked={selectedIds.has(w.id)} onChange={() => toggleSelect(w.id)} /></td>
                  <td style={{ fontFamily: 'monospace', fontWeight: 500 }}>{w.word}</td>
                  <td>
                    <span className={`badge ${w.category === 'blacklist' ? 'badge-error' : 'badge-warning'}`}>
                      {w.category === 'blacklist' ? '黑名单' : '风控词'}
                    </span>
                  </td>
                  <td>{w.scope}</td>
                  <td>{w.createdAt}</td>
                  <td>{w.operator}</td>
                  <td>
                    <button className="btn btn-sm" style={{ color: '#ff4d4f' }} onClick={() => {
                      setWords((prev) => prev.filter((x) => x.id !== w.id));
                      showToast('已删除', 'success');
                    }}>删除</button>
                  </td>
                </tr>
              ))}
              {filteredWords.length === 0 && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: 32, color: '#999' }}>暂无敏感词数据</td></tr>
              )}
            </tbody>
          </table>
        </div>

        <div style={{ marginTop: 12, color: '#999', fontSize: 12 }}>
          支持正则表达式写法（如 微[信信]公[众号汁] 可同时覆盖多种变体）| 每次增删改操作均记录操作日志
        </div>
      </div>

      {showAddModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1001, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', borderRadius: 12, padding: 24, width: 480 }}>
            <h3 style={{ margin: '0 0 16px' }}>➕ 新增敏感词</h3>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>关键词</label>
              <input
                className="config-input"
                type="text"
                value={newWord}
                onChange={(e) => setNewWord(e.target.value)}
                style={{ width: '100%', marginTop: 4 }}
                placeholder="输入关键词或正则表达式"
              />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>类别</label>
              <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                  <input type="radio" name="category" checked={newCategory === 'blacklist'} onChange={() => setNewCategory('blacklist')} />
                  <span style={{ color: '#cf1322' }}>🚫 黑名单（阻断提交）</span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                  <input type="radio" name="category" checked={newCategory === 'risk'} onChange={() => setNewCategory('risk')} />
                  <span style={{ color: '#ad6800' }}>⚠️ 风控词（进入审核）</span>
                </label>
              </div>
            </div>
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>生效范围</label>
              <select
                className="config-input"
                value={newScope}
                onChange={(e) => setNewScope(e.target.value)}
                style={{ width: '100%', marginTop: 4 }}
              >
                {SCOPES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button className="btn btn-sm" onClick={() => { setShowAddModal(false); setNewWord(''); }}>取消</button>
              <button className="btn btn-primary btn-sm" onClick={handleAdd}>确认添加</button>
            </div>
          </div>
        </div>
      )}

      {showImportModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1001, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', borderRadius: 12, padding: 24, width: 480 }}>
            <h3 style={{ margin: '0 0 16px' }}>📥 批量导入敏感词</h3>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>上传TXT文件</label>
              <div style={{ marginTop: 4, padding: 24, border: '2px dashed #d9d9d9', borderRadius: 8, textAlign: 'center', color: '#999', cursor: 'pointer' }}>
                📎 点击或拖拽上传TXT文件<br />
                <span style={{ fontSize: 12 }}>每行一个关键词，系统自动识别换行分隔</span>
              </div>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>导入类别</label>
              <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                  <input type="radio" name="importCategory" defaultChecked />
                  🚫 黑名单
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                  <input type="radio" name="importCategory" />
                  ⚠️ 风控词
                </label>
              </div>
            </div>
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 13, color: '#666', fontWeight: 500 }}>生效范围</label>
              <select className="config-input" style={{ width: '100%', marginTop: 4 }} defaultValue="全部">
                {SCOPES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button className="btn btn-sm" onClick={() => setShowImportModal(false)}>取消</button>
              <button className="btn btn-primary btn-sm" onClick={handleImport}>确认导入</button>
            </div>
          </div>
        </div>
      )}

      {showDeleteConfirm && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1002, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', borderRadius: 12, padding: 24, width: 400 }}>
            <h3 style={{ margin: '0 0 12px' }}>⚠️ 确认删除</h3>
            <p style={{ margin: '0 0 16px', color: '#666' }}>确定要删除选中的 {selectedIds.size} 个关键词吗？此操作不可撤销。</p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button className="btn btn-sm" onClick={() => setShowDeleteConfirm(false)}>取消</button>
              <button className="btn btn-sm" style={{ background: '#ff4d4f', color: '#fff' }} onClick={handleBatchDelete}>确认删除</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
