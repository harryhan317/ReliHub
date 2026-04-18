import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../store/authStore';
import { BottomNav, GuestBanner, SearchBar, SectionHeader } from '../../layouts/Components';
import { Card, Tag } from '../../components/ui/Common';
import { communityService } from '../../services/communityService';
import type { Topic } from '../../types';

const communityCategories = [
  { icon: '🏗️', name: '可靠性设计', color: 'var(--color-accent-light)' },
  { icon: '📡', name: '信号测试', color: 'rgba(245,158,11,0.15)' },
  { icon: '🌡️', name: '环境实验', color: 'rgba(16,185,129,0.15)' },
  { icon: '🔌', name: '元器件', color: 'rgba(239,68,68,0.15)' },
  { icon: '🔬', name: '失效分析', color: 'rgba(139,92,246,0.15)' },
  { icon: '📏', name: '标准解读', color: 'rgba(59,130,246,0.15)' },
  { icon: '✅', name: '质量管理', color: 'rgba(245,158,11,0.15)' },
  { icon: '⚙️', name: '工艺可靠性', color: 'rgba(16,185,129,0.15)' },
  { icon: '📰', name: '行业动态', color: 'rgba(239,68,68,0.15)' },
  { icon: '❓', name: '综合问答', color: 'rgba(139,92,246,0.15)' },
];

const hotTopics = [
  {
    id: '1',
    tags: [{ text: '🏆 悬赏 50🫘', variant: 'gold' as const }, { text: '失效分析', variant: 'accent' as const }, { text: '讨论中', variant: 'warning' as const }],
    title: 'BGA焊点开裂的根因分析方法',
    desc: '产品在温度循环测试后出现BGA焊点开裂，求教各位大佬如何系统性地进行根因分析...',
    replies: 12, likes: 28, views: 456, time: '2小时前',
  },
  {
    id: '2',
    tags: [{ text: '可靠性设计', variant: 'accent' as const }, { text: '已解决', variant: 'success' as const }],
    title: '如何选择合适的降额系数？',
    desc: '不同类型元器件的降额系数选择依据是什么？有没有系统的参考标准？',
    replies: 8, likes: 35, views: 312, time: '昨天',
  },
  {
    id: '3',
    tags: [{ text: '环境实验', variant: 'accent' as const }, { text: '最新', variant: 'warning' as const }, { text: '精华', variant: 'essence' as const }],
    title: '高低温冲击试验的温变率如何确定？',
    desc: '请教各位，在进行高低温冲击试验时，温变率应该根据什么来确定？',
    replies: 5, likes: 19, views: 189, time: '3天前',
  },
];

const CommunityPage: React.FC = () => {
  const navigate = useNavigate();
  const { isGuest } = useAuthStore();
  const [topics, setTopics] = useState<Topic[]>([]);

  useEffect(() => {
    communityService.getTopics({ page: 1, page_size: 10 }).then((res) => {
      if (res.data?.items?.length) setTopics(res.data.items);
    }).catch(() => {});
  }, []);

  return (
    <div className="page active">
      <div className="top-bar">
        <div className="top-bar-title gradient-text">技术社区</div>
        <button className="top-bar-btn" onClick={() => navigate('/community/new-topic')}>✏️</button>
      </div>

      {isGuest && (
        <GuestBanner text="游客模式 · 仅可浏览10条热门话题" onAction={() => navigate('/login')} actionText="注册" icon="👀" />
      )}

      <SearchBar placeholder="搜索话题标题/内容" onSearch={() => navigate('/search')} />

      <div className="content-area" style={{ padding: '0 var(--spacing-lg) var(--spacing-lg)' }}>
        <SectionHeader title="话题分类" />
        <div className="category-grid-5">
          {communityCategories.map((cat, i) => (
            <motion.div
              key={cat.name}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="category-item"
              onClick={() => navigate(`/community/category/${cat.name}`)}
            >
              <div className="category-icon-box" style={{ background: cat.color }}>{cat.icon}</div>
              <div className="category-name">{cat.name}</div>
            </motion.div>
          ))}
        </div>

        <SectionHeader title="🔥 热门话题" />

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
          {hotTopics.map((topic, i) => (
            <motion.div
              key={topic.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.05 }}
            >
              <Card className="topic-card" onClick={() => navigate(`/community/topic/${topic.id}`)}>
                <div className="tag-row">
                  {topic.tags.map((tag) => (
                    <Tag key={tag.text} variant={tag.variant}>{tag.text}</Tag>
                  ))}
                </div>
                <div className="topic-title">{topic.title}</div>
                <div className="topic-desc">{topic.desc}</div>
                <div className="topic-meta">
                  <span>💬 {topic.replies} · 👍 {topic.likes} · 👀 {topic.views}</span>
                  <span>{topic.time}</span>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        <div style={{ height: 80 }} />
      </div>

      <BottomNav activeTab="community" />
    </div>
  );
};

export default CommunityPage;
