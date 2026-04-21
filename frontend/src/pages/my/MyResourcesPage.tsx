import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';
import { Card, Tag } from '../../components/ui/Common';
import { resourceService } from '../../services/resourceService';

const MyResourcesPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const tabs = ['已上传', '已下载'];
  const [uploadedResources, setUploadedResources] = useState<Array<{ id: string; title: string; price: number; download_count: number; tags: Array<{ text: string; variant: 'accent' | 'success' | 'warning' }> }>>([]);
  const [downloadedResources, setDownloadedResources] = useState<Array<{ id: string; title: string; price: number; download_count: number; tags: Array<{ text: string; variant: 'accent' | 'success' | 'warning' }> }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const type = activeTab === 0 ? 'uploaded' : 'downloaded';
    resourceService.getMyResources({ type, page: 1, page_size: 20 }).then((res) => {
      if (res.data?.items) {
        const mapped = res.data.items.map((r: any) => ({
          id: r.id,
          title: r.title,
          price: r.price || 0,
          download_count: r.download_count || 0,
          tags: r.tags?.map((t: any) => ({ text: typeof t === 'string' ? t : t.text, variant: 'accent' as const })) || [],
        }));
        if (activeTab === 0) setUploadedResources(mapped);
        else setDownloadedResources(mapped);
      }
    }).catch(() => {}).finally(() => setLoading(false));
  }, [activeTab]);

  const currentList = activeTab === 0 ? uploadedResources : downloadedResources;

  return (
    <div className="page active">
      <TopBar title="我的资源" />
      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={setActiveTab} />
      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-lg)' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)', color: 'var(--color-text-muted)' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>⏳</div>
            <div>加载中...</div>
          </div>
        ) : currentList.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
            {currentList.map((res) => (
              <Card key={res.id} className="resource-card" onClick={() => navigate(`/resource/${res.id}`)}>
                {res.tags.length > 0 && (
                  <div className="tag-row">
                    {res.tags.map((tag) => <Tag key={tag.text} variant={tag.variant}>{tag.text}</Tag>)}
                  </div>
                )}
                <div className="resource-title">{res.title}</div>
                <div className="resource-meta">
                  <span>📥 {res.download_count}</span>
                  <span className="resource-price">{res.price} 🫘</span>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">📚</div>
            <div className="empty-state-text">{activeTab === 0 ? '暂无上传资源，去分享你的第一个资源吧' : '暂无下载记录'}</div>
            {activeTab === 0 && (
              <button className="btn btn-primary btn-sm" onClick={() => navigate('/resource/upload')}>分享资源</button>
            )}
            {activeTab === 1 && (
              <button className="btn btn-primary btn-sm" onClick={() => navigate('/resource')}>浏览资源</button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyResourcesPage;
