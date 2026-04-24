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

  const handleToggleVisibility = useCallback(async (type: 'resource' | 'community', id: number) => {
    if (type === 'resource') {
      const updated = resourceCats.map((cat) =>
        cat.id === id ? { ...cat, visible: !cat.visible } : cat
      );
      setResourceCats(updated);
      await saveCategories('resource_categories', 'community_categories', updated, communityCats);
    } else {
      const updated = communityCats.map((cat) =>
        cat.id === id ? { ...cat, visible: !cat.visible } : cat
      );
      setCommunityCats(updated);
      await saveCategories('resource_categories', 'community_categories', resourceCats, updated);
    }
  }, [resourceCats, communityCats]);

  const handleEditStart = (cat: CategoryItem) => {
    setEditingId(cat.id || null);
    setEditingName(cat.name);
  };

  const handleEditSave = useCallback(async (type: 'resource' | 'community', id: number) => {
    if (type === 'resource') {
      const updated = resourceCats.map((cat) =>
        cat.id === id ? { ...cat, name: editingName } : cat
      );
      setResourceCats(updated);
      setEditingId(null);
      await saveCategories('resource_categories', 'community_categories', updated, communityCats);
    } else {
      const updated = communityCats.map((cat) =>
        cat.id === id ? { ...cat, name: editingName } : cat
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
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}
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
                <th>分类名称</th>
                <th>资源数</th>
                <th>显示状态</th>
                <th>排序</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {resourceCats.map((cat) => (
                <tr key={cat.id}>
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
                  <td>{cat.sort}</td>
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
                        <button
                          className={`btn btn-sm ${cat.visible ? 'btn-danger' : 'btn-success'}`}
                          onClick={() => handleToggleVisibility('resource', cat.id!)}
                          disabled={saving}
                        >
                          {cat.visible ? '隐藏' : '显示'}
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
              {showAddResource && (
                <tr>
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
                  <td>{resourceCats.length + 1}</td>
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
                <th>分类名称</th>
                <th>话题数</th>
                <th>显示状态</th>
                <th>排序</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {communityCats.map((cat) => (
                <tr key={cat.id}>
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
                  <td>{cat.sort}</td>
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
                        <button
                          className={`btn btn-sm ${cat.visible ? 'btn-danger' : 'btn-success'}`}
                          onClick={() => handleToggleVisibility('community', cat.id!)}
                          disabled={saving}
                        >
                          {cat.visible ? '隐藏' : '显示'}
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
              {showAddCommunity && (
                <tr>
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
                  <td>{communityCats.length + 1}</td>
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
