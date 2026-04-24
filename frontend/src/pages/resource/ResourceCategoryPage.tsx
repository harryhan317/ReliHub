import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';
import { Card, Tag } from '../../components/ui/Common';

const categoryResources: Record<string, Array<{ id: string; title: string; tags: Array<{ text: string; variant: 'accent' | 'success' | 'warning' }>; downloads: number; views: string; price: number }>> = {
  '标准规范': [
    { id: '1', title: 'GJB/Z 299C 电子设备可靠性预计手册', tags: [{ text: '最新', variant: 'warning' }, { text: '基础资源', variant: 'success' }], downloads: 326, views: '1.2k', price: 5 },
    { id: '2', title: 'MIL-HDBK-217F 可靠性预计', tags: [{ text: '最新', variant: 'warning' }], downloads: 210, views: '890', price: 10 },
    { id: '3', title: 'IEC 62380 可靠性数据手册', tags: [], downloads: 156, views: '678', price: 8 },
  ],
};

const ResourceCategoryPage: React.FC = () => {
  const navigate = useNavigate();
  const { category } = useParams();
  const categoryName = category || '全部';
  const [activeTab, setActiveTab] = useState(0);
  const tabs = ['最新', '精华', '基础资源', '闲置'];

  const resources = categoryResources[categoryName] || [];

  return (
    <div className="page active">
      <TopBar title={categoryName} rightContent={
        <button className="top-bar-btn" onClick={() => navigate('/search?type=RESOURCE')}>🔍</button>
      } />
      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={setActiveTab} />
      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-lg)' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
          {resources.length > 0 ? resources.map((res) => (
            <Card key={res.id} className="resource-card" onClick={() => navigate(`/resource/${res.id}`)}>
              {res.tags.length > 0 && (
                <div className="tag-row">
                  {res.tags.map((tag) => <Tag key={tag.text} variant={tag.variant}>{tag.text}</Tag>)}
                </div>
              )}
              <div className="resource-title">{res.title}</div>
              <div className="resource-meta">
                <span>📥 {res.downloads} · 👀 {res.views}</span>
                <span className="resource-price">{res.price} 🫘</span>
              </div>
            </Card>
          )) : (
            <div className="empty-state">
              <div className="empty-state-icon">📂</div>
              <div className="empty-state-text">该分类暂无资源</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResourceCategoryPage;
