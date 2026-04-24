import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { useGuestGuard } from '../../store/useGuestGuard';
import { TopBar } from '../../layouts/Components';
import { Tag, Avatar } from '../../components/ui/Common';
import { Modal } from '../../components/ui/Modal';
import { GuestRegisterModal } from '../../components/ui/GuestRegisterModal';
import { communityService } from '../../services/communityService';

const REPORT_REASONS = [
  '内容违规',
  '恶意攻击',
  '广告灌水',
  '虚假信息',
  '抄袭侵权',
  '其他',
];

const TopicDetailPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { isGuest } = useAuthStore();
  const { showToast } = useUIStore();
  const { checkAction, guideModal, closeGuideModal } = useGuestGuard();

  const [replyContent, setReplyContent] = useState('');
  const [showMore, setShowMore] = useState(false);
  const [liked, setLiked] = useState(false);
  const [followed, setFollowed] = useState(false);
  const [collected, setCollected] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [reportReason, setReportReason] = useState('');
  const [reportDetail, setReportDetail] = useState('');
  const [loading, setLoading] = useState(true);

  const [topic, setTopic] = useState({
    id: id || '1',
    title: 'BGA焊点开裂的根因分析方法',
    content: '产品在温度循环测试后出现BGA焊点开裂，求教各位大佬如何系统性地进行根因分析？目前已做了切片分析，发现开裂位置在IMC层附近，但不确定是工艺问题还是设计问题。有经验的大佬帮忙分析下，谢谢！',
    tags: [{ text: '🏆 悬赏 50🫘', variant: 'gold' as const }, { text: '失效分析', variant: 'accent' as const }, { text: '讨论中', variant: 'warning' as const }],
    author_name: '李工',
    author_level: '熟手',
    reply_count: 12,
    like_count: 28,
    time: '2小时前发布',
  });

  const [replies, setReplies] = useState<Array<{
    id: string; author_name: string; author_level: string;
    content: string; like_count: number; is_best: boolean; time: string;
    avatar_bg: string;
  }>>([
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
  ]);

  useEffect(() => {
    if (id) {
      setLoading(true);
      communityService.getTopic(id).then((res) => {
        if (res.data) {
          const d = res.data;
          setTopic({
            id: d.id,
            title: d.title,
            content: d.content || '',
            tags: d.tags?.map((t: any) => ({ text: typeof t === 'string' ? t : t.text, variant: 'accent' as const })) || [],
            author_name: d.author_name || '匿名',
            author_level: d.author_level || '',
            reply_count: d.reply_count || 0,
            like_count: d.like_count || 0,
            time: d.created_at ? new Date(d.created_at).toLocaleDateString() : '',
          });
          setLiked(false);
          setCollected(false);
        }
      }).catch(() => {}).finally(() => setLoading(false));

      communityService.getReplies(id).then((res) => {
        if (res.data?.items) {
          setReplies(res.data.items.map((r: any) => ({
            id: r.id,
            author_name: r.author_name || '匿名',
            author_level: r.author_level || '',
            content: r.content,
            like_count: r.like_count || 0,
            is_best: r.is_best || false,
            time: r.created_at ? new Date(r.created_at).toLocaleDateString() : '',
            avatar_bg: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
          })));
        }
      }).catch(() => {});
    } else {
      setLoading(false);
    }
  }, [id]);

  const handleReply = async () => {
    if (isGuest) {
      checkAction('reply');
      return;
    }
    if (!replyContent.trim()) {
      showToast('请输入回复内容', 'error');
      return;
    }
    try {
      if (id) await communityService.createReply(id, replyContent);
      showToast('回复成功', 'success');
      setReplyContent('');
      setTopic((prev) => ({ ...prev, reply_count: prev.reply_count + 1 }));
    } catch {
      showToast('回复失败', 'error');
    }
  };

  const handleLike = async () => {
    if (isGuest) {
      checkAction('like');
      return;
    }
    try {
      if (id) await communityService.likeTopic(id);
      setLiked(!liked);
      showToast(liked ? '已取消点赞' : '点赞成功', 'success');
    } catch {
      showToast('操作失败', 'error');
    }
  };

  const handleCollect = async () => {
    if (isGuest) {
      checkAction('collect');
      return;
    }
    try {
      if (id) {
        if (collected) {
          await communityService.uncollectTopic(id);
        } else {
          await communityService.collectTopic(id);
        }
      }
      setCollected(!collected);
      showToast(collected ? '已取消收藏' : '收藏成功', 'success');
    } catch {
      showToast('操作失败', 'error');
    }
  };

  const handleReport = () => {
    if (isGuest) {
      checkAction('report');
      return;
    }
    setShowMore(false);
    setShowReport(true);
  };

  const submitReport = async () => {
    if (!reportReason) {
      showToast('请选择举报原因', 'error');
      return;
    }
    try {
      if (id) await communityService.reportTopic(id, { reason: reportReason, detail: reportDetail });
      showToast('举报已提交，我们会尽快处理', 'success');
      setShowReport(false);
      setReportReason('');
      setReportDetail('');
    } catch {
      showToast('举报提交失败', 'error');
    }
  };

  if (loading) {
    return (
      <div className="page active">
        <TopBar title="话题详情" />
        <div className="content-area-no-nav" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ textAlign: 'center', color: 'var(--color-text-muted)' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>⏳</div>
            <div>加载中...</div>
          </div>
        </div>
      </div>
    );
  }

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
            <button className="icon-btn" onClick={handleLike} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 'var(--font-size-caption)' }}>
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
          <div className="menu-item" onClick={() => { setShowMore(false); handleCollect(); }}>
            <div className="menu-icon" style={{ background: 'rgba(245,158,11,0.15)' }}>⭐</div>
            <span className="menu-text">{collected ? '取消收藏' : '收藏话题'}</span>
          </div>
          <div className="menu-item" onClick={() => { setShowMore(false); showToast('已屏蔽该用户', 'success'); }}>
            <div className="menu-icon" style={{ background: 'rgba(100,116,139,0.15)' }}>🚫</div>
            <span className="menu-text">屏蔽此用户</span>
          </div>
          <div className="menu-item" onClick={handleReport}>
            <div className="menu-icon" style={{ background: 'var(--color-error-bg)' }}>⚠️</div>
            <span className="menu-text">举报</span>
          </div>
        </div>
      </Modal>

      <Modal open={showReport} onClose={() => setShowReport(false)}>
        <div style={{ padding: 'var(--spacing-lg)' }}>
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 700, marginBottom: 'var(--spacing-lg)' }}>举报话题</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
            {REPORT_REASONS.map((reason) => (
              <label key={reason} style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="topic-report-reason"
                  checked={reportReason === reason}
                  onChange={() => setReportReason(reason)}
                  style={{ accentColor: 'var(--color-accent)' }}
                />
                <span style={{ fontSize: 'var(--font-size-body)' }}>{reason}</span>
              </label>
            ))}
          </div>
          <textarea
            className="input-field"
            rows={3}
            placeholder="补充说明（选填）"
            style={{ resize: 'none', marginBottom: 'var(--spacing-lg)' }}
            value={reportDetail}
            onChange={(e) => setReportDetail(e.target.value)}
          />
          <button className="btn btn-primary btn-block" onClick={submitReport}>提交举报</button>
        </div>
      </Modal>

      <GuestRegisterModal
        open={guideModal.open}
        onClose={closeGuideModal}
        source={guideModal.source}
        reason={guideModal.reason}
      />
    </div>
  );
};

export default TopicDetailPage;
