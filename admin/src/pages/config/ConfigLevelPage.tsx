import { useState, useEffect } from 'react';
import { adminService } from '@/services/adminService';

export default function ConfigLevelPage() {
  const [configs, setConfigs] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);

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

  if (loading) return <div className="loading-spinner">加载中...</div>;

  const levels = [
    { name: '新兵', range: '0 ~ 59', perms: '基础功能（AI 10次/天、资源下载、社区发帖）' },
    { name: '老兵', range: '60 ~ 79', perms: '增强功能（AI 30次/天、扩充包购买、悬赏发起）' },
    { name: '专家', range: '80 ~ 100', perms: '完整功能（AI无限、专家标识、优先审核）' },
  ];

  return (
    <div className="config-card">
      <div className="config-card-title">等级体系与信誉分阈值</div>
      <table className="data-table" style={{ boxShadow: 'none' }}>
        <thead>
          <tr>
            <th>等级名称</th>
            <th>信誉分范围</th>
            <th>功能权限</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {levels.map((l) => (
            <tr key={l.name}>
              <td>{l.name}</td>
              <td>{l.range}</td>
              <td>{l.perms}</td>
              <td><button className="btn btn-sm">编辑</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
