import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../store/authStore';
import { useGuestGuard } from '../../store/useGuestGuard';
import { useGuestStore } from '../../store/guestStore';
import { BottomNav, GuestBanner, SearchBar, SectionHeader } from '../../layouts/Components';
import { Card, Tag } from '../../components/ui/Common';
import { GuestRegisterModal } from '../../components/ui/GuestRegisterModal';
import { resourceService } from '../../services/resourceService';
import type { Resource } from '../../types';

const categories = [
  { icon: '📋', name: '标准规范', count: 128 },
  { icon: '📖', name: '器件手册', count: 256 },
  { icon: '📝', name: '应用笔记', count: 89 },
  { icon: '🔧', name: '工具模版', count: 45 },
  { icon: '💡', name: '案例分享', count: 67 },
  { icon: '🎓', name: '培训资料', count: 34 },
  { icon: '📚', name: '推荐书单', count: 22 },
  { icon: '🌐', name: '综合杂谈', count: 15 },
];

const hotResources = [
  {
    id: '1',
    tags: [{ text: '标准规范', variant: 'accent' as const }, { text: '基础资源', variant: 'success' as const }, { text: '最新', variant: 'warning' as const }],
    title: 'GJB/Z 299C 电子设备可靠性预计手册',
    desc: '涵盖元器件计数法和应力分析法，适用于军工及高可靠领域...',
    downloads: 326,
    views: '1.2k',
    price: 5,
  },
  {
    id: '2',
    tags: [{ text: '器件手册', variant: 'accent' as const }],
    title: 'MLCC电容选型与可靠性应用指南',
    desc: '多层陶瓷电容的选型原则、失效模式分析及降额设计建议...',
    downloads: 198,
    views: '856',
    price: 15,
  },
  {
    id: '3',
    tags: [{ text: '案例分享', variant: 'accent' as const }, { text: '精华', variant: 'warning' as const }],
    title: '某型号电源模块HALT测试案例',
    desc: '详细记录了高加速寿命测试全过程，包含失效分析与改进措施...',
    downloads: 145,
    views: '623',
    price: 20,
  },
];

const ResourcePage: React.FC = () => {
  const navigate = useNavigate();
  const { isGuest } = useAuthStore();
  const { checkAction, guideModal, closeGuideModal } = useGuestGuard();
  const guestStore = useGuestStore();
  const [resources, setResources] = useState<Resource[]>([]);

  const handleResourceClick = (id: string) => {
    if (isGuest) {
      if (!checkAction('resource_limit')) return;
      guestStore.incrementResourceView();
    }
    navigate(`/resource/${id}`);
  };

  const handleUpload = () => {
    if (isGuest) {
      checkAction('upload');
      return;
    }
    navigate('/resource/upload');
  };

  useEffect(() => {
    resourceService.getResources({ page: 1, page_size: 10 }).then((res) => {
      if (res.data?.items?.length) setResources(res.data.items);
    }).catch(() => {});
  }, []);

  return (
    <div className="page active">
      <div className="top-bar">
        <div className="top-bar-title gradient-text">资源库</div>
        <button className="top-bar-btn" onClick={handleUpload}>📤</button>
      </div>

      {isGuest && (
        <GuestBanner text="游客模式 · 仅可浏览10条热门资源" onAction={() => navigate('/login')} actionText="注册" icon="👀" />
      )}

      <SearchBar placeholder="搜索资源标题/关键词" onSearch={() => navigate('/search')} />

      <div className="content-area" style={{ padding: '0 var(--spacing-lg) var(--spacing-lg)' }}>
        <SectionHeader title="资源分类" />
        <div className="category-grid-4">
          {categories.map((cat, i) => (
            <motion.div
              key={cat.name}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Card
                className="category-card"
                onClick={() => navigate(`/resource/category/${cat.name}`)}
              >
                <div className="category-icon">{cat.icon}</div>
                <div className="category-name">{cat.name}</div>
                <div className="category-count">{cat.count}</div>
              </Card>
            </motion.div>
          ))}
        </div>

        <SectionHeader title="🔥 热门推荐" />

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
          {hotResources.map((res, i) => (
            <motion.div
              key={res.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.05 }}
            >
              <Card className="resource-card" onClick={() => handleResourceClick(res.id)}>
                <div className="tag-row">
                  {res.tags.map((tag) => (
                    <Tag key={tag.text} variant={tag.variant}>{tag.text}</Tag>
                  ))}
                </div>
                <div className="resource-title">{res.title}</div>
                <div className="resource-desc">{res.desc}</div>
                <div className="resource-meta">
                  <span>📥 {res.downloads} · 👀 {res.views}</span>
                  <span className="resource-price">{res.price} 🫘</span>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        <div style={{ height: 80 }} />
      </div>

      <BottomNav activeTab="resource" />

      <GuestRegisterModal
        open={guideModal.open}
        onClose={closeGuideModal}
        source={guideModal.source}
        reason={guideModal.reason}
      />
    </div>
  );
};

export default ResourcePage;
