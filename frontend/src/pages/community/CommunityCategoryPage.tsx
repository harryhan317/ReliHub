import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';
import { Card, Tag } from '../../components/ui/Common';

const categoryTopics: Record<string, Array<{ id: string; title: string; tags: Array<{ text: string; variant: 'gold' | 'success' | 'warning' | 'accent' }>; replies: number; likes: number; views: number; time: string }>> = {
  '失效分析': [
    { id: '1', title: 'BGA焊点开裂的根因分析方法', tags: [{ text: '🏆 悬赏 50🫘', variant: 'gold' }, { text: '讨论中', variant: 'warning' }], replies: 12, likes: 28, views: 456, time: '2小时前' },
    { id: '2', title: 'ESD失效的典型特征与防护方案', tags: [{ text: '已解决', variant: 'success' }], replies: 6, likes: 22, views: 289, time: '昨天' },
  ],
};

const CommunityCategoryPage: React.FC = () => {
  const navigate = useNavigate();
  const { category } = useParams();
  const categoryName = category || '全部';
  const [activeTab, setActiveTab] = useState(0);
  const tabs = ['最新', '精华', '悬赏', '已解决'];

  const topics = categoryTopics[categoryName] || [];

  return (
    <div className="page active">
      <TopBar title={categoryName} rightContent={
        <button className="top-bar-btn" onClick={() => navigate('/search?type=COMMUNITY')}>🔍</button>
      } />
      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={setActiveTab} />
      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-lg)' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
          {topics.length > 0 ? topics.map((topic) => (
            <Card key={topic.id} className="topic-card" onClick={() => navigate(`/community/topic/${topic.id}`)}>
              {topic.tags.length > 0 && (
                <div className="tag-row">
                  {topic.tags.map((tag) => <Tag key={tag.text} variant={tag.variant}>{tag.text}</Tag>)}
                </div>
              )}
              <div className="topic-title">{topic.title}</div>
              <div className="topic-meta">
                <span>💬 {topic.replies} · 👍 {topic.likes} · 👀 {topic.views}</span>
                <span>{topic.time}</span>
              </div>
            </Card>
          )) : (
            <div className="empty-state">
              <div className="empty-state-icon">💬</div>
              <div className="empty-state-text">该分类暂无话题</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CommunityCategoryPage;
