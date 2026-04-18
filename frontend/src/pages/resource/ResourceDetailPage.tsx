import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { TopBar } from '../../layouts/Components';
import { Card, Tag, Avatar } from '../../components/ui/Common';
import { Modal } from '../../components/ui/Modal';
import { resourceService } from '../../services/resourceService';

const ResourceDetailPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { isGuest } = useAuthStore();
  const { showToast } = useUIStore();
  const [showDownloadConfirm, setShowDownloadConfirm] = useState(false);
  const [liked, setLiked] = useState(false);
  const [collected, setCollected] = useState(false);

  const resource = {
    id: id || '1',
    title: 'GJB/Z 299C 电子设备可靠性预计手册',
    description: '涵盖元器件计数法和应力分析法，适用于军工及高可靠领域的电子设备可靠性预计。包含各类元器件的基本失效率数据及修正因子。',
    tags: [{ text: '标准规范', variant: 'accent' as const }, { text: '基础资源', variant: 'success' as const }, { text: '最新', variant: 'warning' as const }],
    keywords: ['GJB', '可靠性预计', '失效率', '军标'],
    author_name: '张工',
    author_level: '熟手',
    time: '3天前上传',
    download_count: 326,
    view_count: '1,200',
    like_count: 56,
    dislike_count: 2,
    price: 5,
    file_type: 'PDF',
    file_size: '12.5 MB',
  };

  const handleDownload = () => {
    if (isGuest) { showToast('请先登录', 'info'); navigate('/login'); return; }
    setShowDownloadConfirm(true);
  };

  const confirmDownload = async () => {
    try {
      if (id) await resourceService.downloadResource(id);
      showToast('下载成功', 'success');
      setShowDownloadConfirm(false);
    } catch { showToast('下载失败', 'error'); }
  };

  return (
    <div className="page active">
      <TopBar title="资源详情" rightContent={
        <button className="top-bar-btn" onClick={() => { navigator.clipboard.writeText(window.location.href); showToast('链接已复制', 'success'); }}>🔗</button>
      } />
      <div className="content-area-no-nav" style={{ paddingBottom: 0 }}>
        <div style={{ padding: 'var(--spacing-lg)' }}>
          <div className="tag-row" style={{ marginBottom: 'var(--spacing-md)' }}>
            {resource.tags.map((tag) => (
              <Tag key={tag.text} variant={tag.variant}>{tag.text}</Tag>
            ))}
          </div>

          <h2 style={{ fontSize: 'var(--font-size-h2)', fontWeight: 700, marginBottom: 'var(--spacing-sm)' }}>
            {resource.title}
          </h2>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
            <Avatar size="sm">{resource.author_name[0]}</Avatar>
            <div>
              <div style={{ fontSize: 'var(--font-size-caption)', fontWeight: 500 }}>{resource.author_name} · {resource.author_level}</div>
              <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)' }}>{resource.time}</div>
            </div>
          </div>

          <div style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-secondary)', lineHeight: 'var(--line-height-body)', marginBottom: 'var(--spacing-xl)' }}>
            {resource.description}
          </div>

          <div className="tag-row" style={{ flexWrap: 'wrap', marginBottom: 'var(--spacing-xl)' }}>
            {resource.keywords.map((kw) => (
              <Tag key={kw} variant="accent">{kw}</Tag>
            ))}
          </div>

          <Card style={{ marginBottom: 'var(--spacing-lg)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)', fontSize: 'var(--font-size-caption)' }}>
              <div><span style={{ color: 'var(--color-text-muted)' }}>格式</span><br /><strong>{resource.file_type}</strong></div>
              <div><span style={{ color: 'var(--color-text-muted)' }}>大小</span><br /><strong>{resource.file_size}</strong></div>
              <div><span style={{ color: 'var(--color-text-muted)' }}>下载</span><br /><strong>{resource.download_count}次</strong></div>
              <div><span style={{ color: 'var(--color-text-muted)' }}>浏览</span><br /><strong>{resource.view_count}次</strong></div>
            </div>
          </Card>

          <div style={{ display: 'flex', gap: 'var(--spacing-lg)', alignItems: 'center', marginBottom: 'var(--spacing-xl)' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 'var(--font-size-h2)', fontWeight: 700, color: 'var(--color-gold)' }}>{resource.price}</div>
              <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)' }}>可可豆</div>
            </div>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
              <button className="btn btn-primary btn-block" onClick={handleDownload}>📥 立即下载</button>
              <button className="btn btn-secondary btn-block" style={{ fontSize: 'var(--font-size-caption)' }}>👁 预览 (前2页)</button>
            </div>
          </div>

          <div className="divider"></div>

          <div style={{ display: 'flex', justifyContent: 'space-around', padding: 'var(--spacing-md) 0' }}>
            <button className="icon-btn action-col" onClick={() => { if (isGuest) { navigate('/login'); return; } setCollected(!collected); showToast(collected ? '已取消收藏' : '收藏成功', 'success'); }}>
              {collected ? '⭐' : '☆'}<span>{collected ? '已收藏' : '收藏'}</span>
            </button>
            <button className="icon-btn action-col" onClick={() => { if (isGuest) { navigate('/login'); return; } setLiked(!liked); showToast(liked ? '已取消点赞' : '点赞成功', 'success'); }}>
              👍<span>{resource.like_count + (liked ? 1 : 0)}</span>
            </button>
            <button className="icon-btn action-col">👎<span>{resource.dislike_count}</span></button>
            <button className="icon-btn action-col" onClick={() => { navigator.clipboard.writeText(window.location.href); showToast('链接已复制', 'success'); }}>🔗<span>分享</span></button>
          </div>
        </div>
      </div>

      <Modal open={showDownloadConfirm} onClose={() => setShowDownloadConfirm(false)}>
        <div style={{ padding: 'var(--spacing-lg)' }}>
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 600, marginBottom: 'var(--spacing-md)' }}>确认下载</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', padding: 'var(--spacing-md)', background: 'var(--color-bg-input)', borderRadius: 'var(--radius-lg)', marginBottom: 'var(--spacing-lg)' }}>
            <div style={{ fontSize: 24 }}>📄</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 500 }}>{resource.title}</div>
              <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)' }}>{resource.file_type} · {resource.file_size}</div>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)' }}>
            <span style={{ color: 'var(--color-text-tertiary)' }}>下载费用</span>
            <span style={{ fontSize: 'var(--font-size-h3)', fontWeight: 700, color: 'var(--color-gold)' }}>{resource.price} 🫘</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)', fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)' }}>
            <span>当前余额</span>
            <span>50 🫘</span>
          </div>
          <button className="btn btn-primary btn-block btn-lg" onClick={confirmDownload}>确认下载</button>
          <button className="btn btn-secondary btn-block" style={{ marginTop: 'var(--spacing-sm)' }} onClick={() => setShowDownloadConfirm(false)}>取消</button>
        </div>
      </Modal>
    </div>
  );
};

export default ResourceDetailPage;
