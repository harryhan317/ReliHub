import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';
import { Card, Tag } from '../../components/ui/Common';
import { resourceService } from '../../services/resourceService';
import { communityService } from '../../services/communityService';

const MyCollectionsPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const tabs = ['资源', '话题'];
  const [resourceCollections, setResourceCollections] = useState<Array<{ id: string; title: string; price: number; tags: Array<{ text: string; variant: 'accent' | 'success' | 'warning' }> }>>([]);
  const [topicCollections, setTopicCollections] = useState<Array<{ id: string; title: string; reply_count: number; tags: Array<{ text: string; variant: 'accent' | 'success' | 'warning' }> }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    if (activeTab === 0) {
      resourceService.getMyResources({ type: 'collected', page: 1, page_size: 20 }).then((res) => {
        if (res.data?.items) {
          setResourceCollections(res.data.items.map((r: any) => ({
            id: r.id,
            title: r.title,
            price: r.price || 0,
            tags: r.tags?.map((t: any) => ({ text: typeof t === 'string' ? t : t.text, variant: 'accent' as const })) || [],
          })));
        }
      }).catch(() => {}).finally(() => setLoading(false));
    } else {
      communityService.getMyTopics({ type: 'collected', page: 1, page_size: 20 }).then((res) => {
        if (res.data?.items) {
          setTopicCollections(res.data.items.map((t: any) => ({
            id: t.id,
            title: t.title,
            reply_count: t.reply_count || 0,
            tags: t.tags?.map((tag: any) => ({ text: typeof tag === 'string' ? tag : tag.text, variant: 'accent' as const })) || [],
          })));
        }
      }).catch(() => {}).finally(() => setLoading(false));
    }
  }, [activeTab]);

  return (
    <div className="page active">
      <TopBar title="我的收藏" />
      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={setActiveTab} />
      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-lg)' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)', color: 'var(--color-text-muted)' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>⏳</div>
            <div>加载中...</div>
          </div>
        ) : activeTab === 0 ? (
          resourceCollections.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              {resourceCollections.map((res) => (
                <Card key={res.id} className="resource-card" onClick={() => navigate(`/resource/${res.id}`)}>
                  {res.tags.length > 0 && (
                    <div className="tag-row">
                      {res.tags.map((tag) => <Tag key={tag.text} variant={tag.variant}>{tag.text}</Tag>)}
                    </div>
                  )}
                  <div className="resource-title">{res.title}</div>
                  <div className="resource-meta">
                    <span></span>
                    <span className="resource-price">{res.price} 🫘</span>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">⭐</div>
              <div className="empty-state-text">暂无收藏资源</div>
              <button className="btn btn-primary btn-sm" onClick={() => navigate('/resource')}>浏览资源</button>
            </div>
          )
        ) : (
          topicCollections.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              {topicCollections.map((topic) => (
                <Card key={topic.id} className="topic-card" onClick={() => navigate(`/community/topic/${topic.id}`)}>
                  {topic.tags.length > 0 && (
                    <div className="tag-row">
                      {topic.tags.map((tag) => <Tag key={tag.text} variant={tag.variant}>{tag.text}</Tag>)}
                    </div>
                  )}
                  <div className="topic-title">{topic.title}</div>
                  <div className="topic-meta">
                    <span>💬 {topic.reply_count} 回复</span>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">⭐</div>
              <div className="empty-state-text">暂无收藏话题</div>
              <button className="btn btn-primary btn-sm" onClick={() => navigate('/community')}>浏览社区</button>
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default MyCollectionsPage;
