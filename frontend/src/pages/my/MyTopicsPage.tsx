import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';
import { Card, Tag } from '../../components/ui/Common';
import { communityService } from '../../services/communityService';

const MyTopicsPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const tabs = ['我发起的', '我回复的'];
  const [myTopics, setMyTopics] = useState<Array<{ id: string; title: string; reply_count: number; like_count: number; tags: Array<{ text: string; variant: 'accent' | 'success' | 'warning' }> }>>([]);
  const [repliedTopics, setRepliedTopics] = useState<Array<{ id: string; title: string; reply_count: number; like_count: number; tags: Array<{ text: string; variant: 'accent' | 'success' | 'warning' }> }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const type = activeTab === 0 ? 'created' : 'replied';
    communityService.getMyTopics({ type, page: 1, page_size: 20 }).then((res) => {
      if (res.data?.items) {
        const mapped = res.data.items.map((t: any) => ({
          id: t.id,
          title: t.title,
          reply_count: t.reply_count || 0,
          like_count: t.like_count || 0,
          tags: t.tags?.map((tag: any) => ({ text: typeof tag === 'string' ? tag : tag.text, variant: 'accent' as const })) || [],
        }));
        if (activeTab === 0) setMyTopics(mapped);
        else setRepliedTopics(mapped);
      }
    }).catch(() => {}).finally(() => setLoading(false));
  }, [activeTab]);

  const currentList = activeTab === 0 ? myTopics : repliedTopics;

  return (
    <div className="page active">
      <TopBar title="我的话题" />
      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={setActiveTab} />
      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-lg)' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)', color: 'var(--color-text-muted)' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>⏳</div>
            <div>加载中...</div>
          </div>
        ) : currentList.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
            {currentList.map((topic) => (
              <Card key={topic.id} className="topic-card" onClick={() => navigate(`/community/topic/${topic.id}`)}>
                {topic.tags.length > 0 && (
                  <div className="tag-row">
                    {topic.tags.map((tag) => <Tag key={tag.text} variant={tag.variant}>{tag.text}</Tag>)}
                  </div>
                )}
                <div className="topic-title">{topic.title}</div>
                <div className="topic-meta">
                  <span>💬 {topic.reply_count} · 👍 {topic.like_count}</span>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">💬</div>
            <div className="empty-state-text">{activeTab === 0 ? '暂无发起的话题' : '暂无回复的话题'}</div>
            <button className="btn btn-primary btn-sm" onClick={() => navigate('/community')}>浏览社区</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyTopicsPage;
