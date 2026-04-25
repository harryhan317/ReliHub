import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';

interface CategoryItem {
  id?: number;
  name: string;
  count: number;
  visible: boolean;
  sort: number;
}

export default function ConfigCategoryPage() {
  const [resourceCats, setResourceCats] = useState<CategoryItem[]>([]);
  const [communityCats, setCommunityCats] = useState<CategoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingName, setEditingName] = useState('');
  const [showAddResource, setShowAddResource] = useState(false);
  const [showAddCommunity, setShowAddCommunity] = useState(false);
  const [newResourceName, setNewResourceName] = useState('');
  const [newCommunityName, setNewCommunityName] = useState('');
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [confirmData, setConfirmData] = useState<{type: 'resource' | 'community', id: number, name: string} | null>(null);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    setLoading(true);
    try {
      const res = await adminService.getSystemConfigs();
      const configMap: Record<string, string> = {};
      res.configs?.forEach((item) => { configMap[item.config_key] = item.config_value; });

      if (configMap.resource_categories) {
        setResourceCats(JSON.parse(configMap.resource_categories));
      } else {
        setResourceCats([
          { id: 1, name: '标准规范', count: 45, visible: true, sort: 1 },
          { id: 2, name: '器件手册', count: 38, visible: true, sort: 2 },
          { id: 3, name: '应用笔记', count: 52, visible: true, sort: 3 },
          { id: 4, name: '工具模版', count: 23, visible: true, sort: 4 },
          { id: 5, name: '案例分享', count: 31, visible: true, sort: 5 },
          { id: 6, name: '培训资料', count: 18, visible: false, sort: 6 },
        ]);
      }

      if (configMap.community_categories) {
        setCommunityCats(JSON.parse(configMap.community_categories));
      } else {
        setCommunityCats([
          { id: 1, name: '可靠性设计', count: 89, visible: true, sort: 1 },
          { id: 2, name: '信号测试', count: 56, visible: true, sort: 2 },
          { id: 3, name: '环境实验', count: 42, visible: true, sort: 3 },
          { id: 4, name: '元器件', count: 67, visible: true, sort: 4 },
          { id: 5, name: '失效分析', count: 34, visible: true, sort: 5 },
        ]);
      }
    } catch {
      showToast('加载分类数据失败', 'error');
    } finally {
      setLoading(false);
    }
  };

  const saveCategories = async (resourceKey: string, communityKey: string, resourceData: CategoryItem[], communityData: CategoryItem[]) => {
    setSaving(true);
    try {
      await adminService.updateSystemConfig(resourceKey, JSON.stringify(resourceData));
      await adminService.updateSystemConfig(communityKey, JSON.stringify(communityData));
      showToast('分类配置已保存', 'success');
    } catch {
      showToast('保存失败', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteCategory = (type: 'resource' | 'community', id: number) => {
    const categories = type === 'resource' ? resourceCats : communityCats;
    const category = categories.find(cat => cat.id === id);
    
    if (!category) return;
    
    // 检查资源数或话题数
    if (category.count > 0) {
      const categoryType = type === 'resource' ? '资源' : '话题';
      showToast(`该分类下存在${categoryType}，不可隐藏或删除`, 'error');
      return;
    }
    
    // 显示自定义确认对话框
    setConfirmData({ type, id, name: category.name });
    setShowConfirmDialog(true);
  };

  const handleConfirmDelete = () => {
    if (!confirmData) return;
    
    const { type, id } = confirmData;
    
    if (type === 'resource') {
      const updated = resourceCats.filter(cat => cat.id !== id);
      setResourceCats(updated);
      saveCategories('resource_categories', 'community_categories', updated, communityCats);
    } else {
      const updated = communityCats.filter(cat => cat.id !== id);
      setCommunityCats(updated);
      saveCategories('resource_categories', 'community_categories', resourceCats, updated);
    }
    
    setShowConfirmDialog(false);
    setConfirmData(null);
  };

  const handleCancelDelete = () => {
    setShowConfirmDialog(false);
    setConfirmData(null);
  };

  const handleToggleVisibility = (type: 'resource' | 'community', id: number) => {
    const categories = type === 'resource' ? resourceCats : communityCats;
    const category = categories.find(cat => cat.id === id);
    
    if (!category) return;
    
    // 检查资源数或话题数
    if (category.count > 0) {
      const categoryType = type === 'resource' ? '资源' : '话题';
      showToast(`该分类下存在${categoryType}，不可隐藏或删除`, 'error');
      return;
    }
    
    if (type === 'resource') {
      const updated = resourceCats.map((cat) =>
        cat.id === id ? { ...cat, visible: !cat.visible } : cat
      );
      setResourceCats(updated);
      saveCategories('resource_categories', 'community_categories', updated, communityCats);
    } else {
      const updated = communityCats.map((cat) =>
        cat.id === id ? { ...cat, visible: !cat.visible } : cat
      );
      setCommunityCats(updated);
      saveCategories('resource_categories', 'community_categories', resourceCats, updated);
    }
  };

  const handleEditStart = (cat: CategoryItem) => {
    setEditingId(cat.id || null);
    setEditingName(cat.name);
  };

  const checkDuplicateName = (type: 'resource' | 'community', name: string, excludeId?: number): boolean => {
    const categories = type === 'resource' ? resourceCats : communityCats;
    const normalizedNewName = name.trim().toLowerCase();
    
    return categories.some(cat => {
      if (excludeId && cat.id === excludeId) return false;
      return cat.name.toLowerCase() === normalizedNewName;
    });
  };

  const handleEditSave = useCallback(async (type: 'resource' | 'community', id: number) => {
    if (!editingName.trim()) {
      showToast('请输入分类名称', 'error');
      return;
    }

    // 检查重复名称
    if (checkDuplicateName(type, editingName, id)) {
      showToast('分类名称已存在，请使用其他名称', 'error');
      return;
    }

    if (type === 'resource') {
      const updated = resourceCats.map((cat) =>
        cat.id === id ? { ...cat, name: editingName.trim() } : cat
      );
      setResourceCats(updated);
      setEditingId(null);
      await saveCategories('resource_categories', 'community_categories', updated, communityCats);
    } else {
      const updated = communityCats.map((cat) =>
        cat.id === id ? { ...cat, name: editingName.trim() } : cat
      );
      setCommunityCats(updated);
      setEditingId(null);
      await saveCategories('resource_categories', 'community_categories', resourceCats, updated);
    }
  }, [editingName, resourceCats, communityCats]);

  const handleAddResource = useCallback(async () => {
    if (!newResourceName.trim()) {
      showToast('请输入分类名称', 'error');
      return;
    }

    // 检查重复名称
    if (checkDuplicateName('resource', newResourceName)) {
      showToast('分类名称已存在，请使用其他名称', 'error');
      return;
    }

    const newCat: CategoryItem = {
      id: Date.now(),
      name: newResourceName.trim(),
      count: 0,
      visible: true,
      sort: resourceCats.length + 1,
    };
    const updated = [...resourceCats, newCat];
    setResourceCats(updated);
    setNewResourceName('');
    setShowAddResource(false);
    await saveCategories('resource_categories', 'community_categories', updated, communityCats);
  }, [newResourceName, resourceCats, communityCats]);

  const handleAddCommunity = useCallback(async () => {
    if (!newCommunityName.trim()) {
      showToast('请输入分类名称', 'error');
      return;
    }

    // 检查重复名称
    if (checkDuplicateName('community', newCommunityName)) {
      showToast('分类名称已存在，请使用其他名称', 'error');
      return;
    }

    const newCat: CategoryItem = {
      id: Date.now(),
      name: newCommunityName.trim(),
      count: 0,
      visible: true,
      sort: communityCats.length + 1,
    };
    const updated = [...communityCats, newCat];
    setCommunityCats(updated);
    setNewCommunityName('');
    setShowAddCommunity(false);
    await saveCategories('resource_categories', 'community_categories', resourceCats, updated);
  }, [newCommunityName, resourceCats, communityCats]);

  const handleMoveUp = (type: 'resource' | 'community', index: number) => {
    if (index === 0) return;
    
    const cats = type === 'resource' ? [...resourceCats] : [...communityCats];
    if (index > 0 && index < cats.length) {
      const temp = cats[index]!;
      cats[index] = cats[index - 1]!;
      cats[index - 1] = temp;
    }
    
    if (type === 'resource') {
      setResourceCats(cats);
      saveCategories('resource_categories', 'community_categories', cats, communityCats);
    } else {
      setCommunityCats(cats);
      saveCategories('resource_categories', 'community_categories', resourceCats, cats);
    }
  };

  const handleMoveDown = (type: 'resource' | 'community', index: number) => {
    const cats = type === 'resource' ? [...resourceCats] : [...communityCats];
    if (index < cats.length - 1) {
      const temp = cats[index]!;
      cats[index] = cats[index + 1]!;
      cats[index + 1] = temp;
    }
    
    if (type === 'resource') {
      setResourceCats(cats);
      saveCategories('resource_categories', 'community_categories', cats, communityCats);
    } else {
      setCommunityCats(cats);
      saveCategories('resource_categories', 'community_categories', resourceCats, cats);
    }
  };

  const handleCancelAdd = (type: 'resource' | 'community') => {
    if (type === 'resource') {
      setShowAddResource(false);
      setNewResourceName('');
    } else {
      setShowAddCommunity(false);
      setNewCommunityName('');
    }
  };

  if (loading) return <div className="loading-spinner">加载中...</div>;

  return (
    <>
      {toast && (
        <div 
          className={`toast toast-${toast.type}`}
          style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: 9999,
            padding: '12px 20px',
            borderRadius: '4px',
            color: 'white',
            fontWeight: 'bold',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            backgroundColor: toast.type === 'success' ? '#28a745' : '#dc3545'
          }}
        >
          {toast.msg}
        </div>
      )}
      
      {showConfirmDialog && confirmData && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10000
          }}
        >
          <div 
            style={{
              backgroundColor: 'white',
              padding: '24px',
              borderRadius: '8px',
              boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
              minWidth: '400px',
              maxWidth: '500px'
            }}
          >
            <h3 style={{ margin: '0 0 16px 0', color: '#333' }}>确认删除</h3>
            <p style={{ margin: '0 0 24px 0', color: '#666', lineHeight: '1.5' }}>
              确定要删除分类"{confirmData.name}"吗？请谨慎操作
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button 
                className="btn btn-sm"
                onClick={handleCancelDelete}
                style={{ padding: '8px 16px' }}
              >
                取消
              </button>
              <button 
                className="btn btn-sm btn-warning"
                onClick={handleConfirmDelete}
                style={{ padding: '8px 16px' }}
              >
                确定删除
              </button>
            </div>
          </div>
        </div>
      )}
      
      <div className="config-grid">
        <div className="config-card">
          <div className="config-card-title">
            资源分类管理
            <button
              className="btn btn-primary btn-sm"
              style={{ float: 'right' }}
              onClick={() => setShowAddResource(true)}
              disabled={saving}
            >
              + 新增分类
            </button>
          </div>
          <table className="data-table" style={{ boxShadow: 'none' }}>
            <thead>
              <tr>
                <th>序号</th>
                <th>分类名称</th>
                <th>资源数</th>
                <th>显示状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {resourceCats.map((cat, index) => (
                <tr key={cat.id}>
                  <td>{index + 1}</td>
                  <td>
                    {editingId === cat.id ? (
                      <input
                        className="config-input"
                        type="text"
                        value={editingName}
                        onChange={(e) => setEditingName(e.target.value)}
                        style={{ width: 120 }}
                        autoFocus
                      />
                    ) : (
                      cat.name
                    )}
                  </td>
                  <td>{cat.count}</td>
                  <td><span className={`badge ${cat.visible ? 'badge-success' : 'badge-default'}`}>{cat.visible ? '显示' : '隐藏'}</span></td>
                  <td>
                    {editingId === cat.id ? (
                      <>
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => handleEditSave('resource', cat.id!)}
                          disabled={saving}
                        >
                          保存
                        </button>
                        <button
                          className="btn btn-sm"
                          onClick={() => setEditingId(null)}
                          disabled={saving}
                        >
                          取消
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          className="btn btn-sm"
                          onClick={() => handleEditStart(cat)}
                          disabled={saving}
                        >
                          编辑
                        </button>
                        <span style={{ marginRight: '5px' }}></span>
                        <button
                          className={`btn btn-sm ${cat.visible ? 'btn-danger' : 'btn-success'}`}
                          onClick={() => handleToggleVisibility('resource', cat.id!)}
                          disabled={saving}
                          title={cat.count > 0 ? '该分类下存在资源，不可隐藏或删除' : ''}
                        >
                          {cat.visible ? '隐藏' : '显示'}
                        </button>
                        <span style={{ marginRight: '5px' }}></span>
                        <button
                          className="btn btn-sm btn-warning"
                          onClick={() => handleDeleteCategory('resource', cat.id!)}
                          disabled={saving}
                          title={cat.count > 0 ? '该分类下存在资源，不可隐藏或删除' : ''}
                        >
                          删除
                        </button>
                        <span style={{ marginLeft: '5px' }}>
                          <button
                            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#666', fontSize: '16px', padding: '2px' }}
                            onClick={() => handleMoveUp('resource', index)}
                            disabled={index === 0}
                            title="上移"
                          >
                            ↑
                          </button>
                          <button
                            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#666', fontSize: '16px', padding: '2px' }}
                            onClick={() => handleMoveDown('resource', index)}
                            disabled={index === resourceCats.length - 1}
                            title="下移"
                          >
                            ↓
                          </button>
                        </span>
                      </>
                    )}
                  </td>
                </tr>
              ))}
              {showAddResource && (
                <tr>
                  <td>{resourceCats.length + 1}</td>
                  <td>
                    <input
                      className="config-input"
                      type="text"
                      value={newResourceName}
                      onChange={(e) => setNewResourceName(e.target.value)}
                      placeholder="输入分类名称"
                      style={{ width: 120 }}
                      autoFocus
                    />
                  </td>
                  <td>0</td>
                  <td><span className="badge badge-success">显示</span></td>
                  <td>
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={handleAddResource}
                      disabled={saving}
                    >
                      保存
                    </button>
                    <button
                      className="btn btn-sm"
                      onClick={() => handleCancelAdd('resource')}
                      disabled={saving}
                    >
                      取消
                    </button>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="config-card">
          <div className="config-card-title">
            社区分类管理
            <button
              className="btn btn-primary btn-sm"
              style={{ float: 'right' }}
              onClick={() => setShowAddCommunity(true)}
              disabled={saving}
            >
              + 新增分类
            </button>
          </div>
          <table className="data-table" style={{ boxShadow: 'none' }}>
            <thead>
              <tr>
                <th>序号</th>
                <th>分类名称</th>
                <th>话题数</th>
                <th>显示状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {communityCats.map((cat, index) => (
                <tr key={cat.id}>
                  <td>{index + 1}</td>
                  <td>
                    {editingId === cat.id ? (
                      <input
                        className="config-input"
                        type="text"
                        value={editingName}
                        onChange={(e) => setEditingName(e.target.value)}
                        style={{ width: 120 }}
                        autoFocus
                      />
                    ) : (
                      cat.name
                    )}
                  </td>
                  <td>{cat.count}</td>
                  <td><span className={`badge ${cat.visible ? 'badge-success' : 'badge-default'}`}>{cat.visible ? '显示' : '隐藏'}</span></td>
                  <td>
                    {editingId === cat.id ? (
                      <>
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => handleEditSave('community', cat.id!)}
                          disabled={saving}
                        >
                          保存
                        </button>
                        <button
                          className="btn btn-sm"
                          onClick={() => setEditingId(null)}
                          disabled={saving}
                        >
                          取消
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          className="btn btn-sm"
                          onClick={() => handleEditStart(cat)}
                          disabled={saving}
                        >
                          编辑
                        </button>
                        <span style={{ marginRight: '5px' }}></span>
                        <button
                          className={`btn btn-sm ${cat.visible ? 'btn-danger' : 'btn-success'}`}
                          onClick={() => handleToggleVisibility('community', cat.id!)}
                          disabled={saving}
                          title={cat.count > 0 ? '该分类下存在话题，不可隐藏或删除' : ''}
                        >
                          {cat.visible ? '隐藏' : '显示'}
                        </button>
                        <span style={{ marginRight: '5px' }}></span>
                        <button
                          className="btn btn-sm btn-warning"
                          onClick={() => handleDeleteCategory('community', cat.id!)}
                          disabled={saving}
                          title={cat.count > 0 ? '该分类下存在话题，不可隐藏或删除' : ''}
                        >
                          删除
                        </button>
                        <span style={{ marginLeft: '5px' }}>
                          <button
                            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#666', fontSize: '16px', padding: '2px' }}
                            onClick={() => handleMoveUp('community', index)}
                            disabled={index === 0}
                            title="上移"
                          >
                            ↑
                          </button>
                          <button
                            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#666', fontSize: '16px', padding: '2px' }}
                            onClick={() => handleMoveDown('community', index)}
                            disabled={index === communityCats.length - 1}
                            title="下移"
                          >
                            ↓
                          </button>
                        </span>
                      </>
                    )}
                  </td>
                </tr>
              ))}
              {showAddCommunity && (
                <tr>
                  <td>{communityCats.length + 1}</td>
                  <td>
                    <input
                      className="config-input"
                      type="text"
                      value={newCommunityName}
                      onChange={(e) => setNewCommunityName(e.target.value)}
                      placeholder="输入分类名称"
                      style={{ width: 120 }}
                      autoFocus
                    />
                  </td>
                  <td>0</td>
                  <td><span className="badge badge-success">显示</span></td>
                  <td>
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={handleAddCommunity}
                      disabled={saving}
                    >
                      保存
                    </button>
                    <button
                      className="btn btn-sm"
                      onClick={() => handleCancelAdd('community')}
                      disabled={saving}
                    >
                      取消
                    </button>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
