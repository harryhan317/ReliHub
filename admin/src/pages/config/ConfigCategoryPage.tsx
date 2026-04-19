import { useState } from 'react';

interface CategoryItem {
  name: string;
  count: number;
  visible: boolean;
  sort: number;
}

const initialResourceCategories: CategoryItem[] = [
  { name: '标准规范', count: 45, visible: true, sort: 1 },
  { name: '器件手册', count: 38, visible: true, sort: 2 },
  { name: '应用笔记', count: 52, visible: true, sort: 3 },
  { name: '工具模版', count: 23, visible: true, sort: 4 },
  { name: '案例分享', count: 31, visible: true, sort: 5 },
  { name: '培训资料', count: 18, visible: false, sort: 6 },
];

const initialCommunityCategories: CategoryItem[] = [
  { name: '可靠性设计', count: 89, visible: true, sort: 1 },
  { name: '信号测试', count: 56, visible: true, sort: 2 },
  { name: '环境实验', count: 42, visible: true, sort: 3 },
  { name: '元器件', count: 67, visible: true, sort: 4 },
  { name: '失效分析', count: 34, visible: true, sort: 5 },
];

export default function ConfigCategoryPage() {
  const [resourceCats] = useState(initialResourceCategories);
  const [communityCats] = useState(initialCommunityCategories);

  return (
    <div className="config-grid">
      <div className="config-card">
        <div className="config-card-title">
          资源分类管理
          <button className="btn btn-primary btn-sm" style={{ float: 'right' }}>+ 新增分类</button>
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
              <tr key={cat.name}>
                <td>{cat.name}</td>
                <td>{cat.count}</td>
                <td><span className={`badge ${cat.visible ? 'badge-success' : 'badge-default'}`}>{cat.visible ? '显示' : '隐藏'}</span></td>
                <td>{cat.sort}</td>
                <td>
                  <button className="btn btn-sm">编辑</button>{' '}
                  <button className={`btn btn-sm ${cat.visible ? 'btn-danger' : 'btn-success'}`}>{cat.visible ? '隐藏' : '显示'}</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="config-card">
        <div className="config-card-title">
          社区分类管理
          <button className="btn btn-primary btn-sm" style={{ float: 'right' }}>+ 新增分类</button>
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
              <tr key={cat.name}>
                <td>{cat.name}</td>
                <td>{cat.count}</td>
                <td><span className={`badge ${cat.visible ? 'badge-success' : 'badge-default'}`}>{cat.visible ? '显示' : '隐藏'}</span></td>
                <td>{cat.sort}</td>
                <td>
                  <button className="btn btn-sm">编辑</button>{' '}
                  <button className={`btn btn-sm ${cat.visible ? 'btn-danger' : 'btn-success'}`}>{cat.visible ? '隐藏' : '显示'}</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
