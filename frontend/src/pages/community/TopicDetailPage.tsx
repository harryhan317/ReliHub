import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { TopBar } from '../../layouts/Components';
import { Tag, Avatar } from '../../components/ui/Common';
import { Modal } from '../../components/ui/Modal';

const TopicDetailPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { isGuest } = useAuthStore();
  const { showToast } = useUIStore();
  const [replyContent, setReplyContent] = useState('');
  const [showMore, setShowMore] = useState(false);
  const [liked, setLiked] = useState(false);
  const [followed, setFollowed] = useState(false);
  const [collected, setCollected] = useState(false);

  const topic = {
    id: id || '1',
    title: 'BGA焊点开裂的根因分析方法',
    content: '产品在温度循环测试后出现BGA焊点开裂，求教各位大佬如何系统性地进行根因分析？目前已做了切片分析，发现开裂位置在IMC层附近，但不确定是工艺问题还是设计问题。有经验的大佬帮忙分析下，谢谢！',
    tags: [{ text: '🏆 悬赏 50🫘', variant: 'gold' as const }, { text: '失效分析', variant: 'accent' as const }, { text: '讨论中', variant: 'warning' as const }],
    author_name: '李工',
    author_level: '熟手',
    reply_count: 12,
    like_count: 28,
    dislike_count: 1,
    time: '2小时前发布',
  };

  const replies = [
    {
      id: 'r1', author_name: '王专家', author_level: '老炮',
      content: 'IMC层开裂通常与以下因素有关：1. 回流焊温度曲线不合理导致IMC过厚；2. PCB焊盘设计不满足BGA要求；3. 材料CTE不匹配。建议先检查回流焊曲线和IMC厚度...',
      like_count: 15, is_best: true, time: '1小时前',
      avatar_bg: 'linear-gradient(135deg,#10b981,#059669)',
    },
    {
      id: 'r2', author_name: '陈工', author_level: '入门',
      content: '补充一点，如果是无铅工艺，SAC305焊料的IMC生长特性与有铅差异很大，建议做EDS成分分析确认IMC类型。',
      like_count: 8, is_best: false, time: '45分钟前',
      avatar_bg: 'linear-gradient(135deg,#f59e0b,#d97706)',
    },
  ];

  const handleReply = () => {
    if (isGuest) { showToast('请先登录', 'info'); navigate('/login'); return; }
    if (!replyContent.trim()) { showToast('请输入回复内容', 'error'); return; }
    showToast('回复成功', 'success');
    setReplyContent('');
  };

  return (
    <div className="page active">
      <TopBar title="话题详情" rightContent={
        <button className="top-bar-btn" onClick={() => setShowMore(true)}>⋯</button>
      } />
      <div className="content-area-no-nav" style={{ paddingBottom: 80 }}>
        <div style={{ padding: 'var(--spacing-lg)' }}>
          <div className="tag-row" style={{ marginBottom: 'var(--spacing-md)' }}>
            {topic.tags.map((tag) => (
              <Tag key={tag.text} variant={tag.variant}>{tag.text}</Tag>
            ))}
          </div>

          <h2 style={{ fontSize: 'var(--font-size-h2)', fontWeight: 700, marginBottom: 'var(--spacing-md)' }}>
            {topic.title}
          </h2>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
            <Avatar size="sm">{topic.author_name[0]}</Avatar>
            <div>
              <div style={{ fontSize: 'var(--font-size-caption)', fontWeight: 500 }}>{topic.author_name} · {topic.author_level}</div>
              <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)' }}>{topic.time}</div>
            </div>
          </div>

          <div style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-secondary)', lineHeight: 'var(--line-height-body)', marginBottom: 'var(--spacing-xl)' }}>
            {topic.content}
          </div>

          <div className="topic-actions">
            <button className="icon-btn" onClick={() => setLiked(!liked)} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 'var(--font-size-caption)' }}>
              👍 {topic.like_count + (liked ? 1 : 0)}
            </button>
            <button className="icon-btn" style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 'var(--font-size-caption)' }}>
              👎 {topic.dislike_count}
            </button>
            <button className={`btn ${followed ? 'btn-primary' : 'btn-ghost'} btn-sm`} onClick={() => setFollowed(!followed)}>
              {followed ? '已关注' : '+关注'}
            </button>
            <button className="icon-btn" onClick={() => { navigator.clipboard.writeText(window.location.href); showToast('链接已复制', 'success'); }} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 'var(--font-size-caption)' }}>
              🔗 分享
            </button>
          </div>

          <div className="section-header" style={{ paddingLeft: 0, paddingRight: 0, marginTop: 'var(--spacing-lg)' }}>
            <div className="section-title">回复 ({topic.reply_count})</div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-lg)' }}>
            {replies.map((reply) => (
              <div key={reply.id} className="reply-item">
                <Avatar size="sm" style={{ background: reply.avatar_bg }}>{reply.author_name[0]}</Avatar>
                <div className="reply-content">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: 'var(--font-size-caption)', fontWeight: 500 }}>{reply.author_name} · {reply.author_level}</span>
                    {reply.is_best && <Tag variant="success" style={{ fontSize: 10 }}>✓ 最佳回答</Tag>}
                  </div>
                  <div className="reply-text">{reply.content}</div>
                  <div className="reply-meta">
                    <span>👍 {reply.like_count}</span>
                    <span>{reply.time}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="chat-input-bar-no-nav" style={{ bottom: 'var(--safe-area-bottom)' }}>
        <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'center' }}>
          <input
            className="input-field"
            style={{ flex: 1, borderRadius: 'var(--radius-pill)', padding: '10px 16px' }}
            placeholder="写回复..."
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleReply()}
          />
          <button className="btn btn-primary btn-sm" onClick={handleReply}>发送</button>
        </div>
      </div>

      <Modal open={showMore} onClose={() => setShowMore(false)}>
        <div style={{ padding: 'var(--spacing-lg)' }}>
          <div className="menu-item" onClick={() => { setShowMore(false); navigator.clipboard.writeText(window.location.href); showToast('链接已复制', 'success'); }}>
            <div className="menu-icon" style={{ background: 'var(--color-accent-light)' }}>🔗</div>
            <span className="menu-text">分享话题</span>
          </div>
          <div className="menu-item" onClick={() => { setShowMore(false); setCollected(!collected); showToast(collected ? '已取消收藏' : '收藏成功', 'success'); }}>
            <div className="menu-icon" style={{ background: 'rgba(245,158,11,0.15)' }}>⭐</div>
            <span className="menu-text">收藏话题</span>
          </div>
          <div className="menu-item" onClick={() => { setShowMore(false); showToast('已屏蔽该用户', 'success'); }}>
            <div className="menu-icon" style={{ background: 'rgba(100,116,139,0.15)' }}>🚫</div>
            <span className="menu-text">屏蔽此用户</span>
          </div>
          <div className="menu-item" onClick={() => { setShowMore(false); showToast('举报已提交', 'success'); }}>
            <div className="menu-icon" style={{ background: 'var(--color-error-bg)' }}>⚠️</div>
            <span className="menu-text">举报</span>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default TopicDetailPage;
