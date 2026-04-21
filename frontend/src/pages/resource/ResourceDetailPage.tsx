import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { useGuestGuard } from '../../store/useGuestGuard';
import { TopBar } from '../../layouts/Components';
import { Card, Tag, Avatar } from '../../components/ui/Common';
import { Modal } from '../../components/ui/Modal';
import { GuestRegisterModal } from '../../components/ui/GuestRegisterModal';
import { resourceService } from '../../services/resourceService';

const REPORT_REASONS = [
  '内容违规',
  '侵犯版权',
  '虚假信息',
  '重复资源',
  '分类错误',
  '其他',
];

const ResourceDetailPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { isGuest, user } = useAuthStore();
  const { showToast } = useUIStore();
  const { checkAction, guideModal, closeGuideModal } = useGuestGuard();

  const [showDownloadConfirm, setShowDownloadConfirm] = useState(false);
  const [liked, setLiked] = useState(false);
  const [collected, setCollected] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [reportReason, setReportReason] = useState('');
  const [reportDetail, setReportDetail] = useState('');
  const [loading, setLoading] = useState(true);

  const [resource, setResource] = useState({
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
  });

  useEffect(() => {
    if (id) {
      setLoading(true);
      resourceService.getResource(id).then((res) => {
        if (res.data) {
          const d = res.data;
          setResource({
            id: d.id,
            title: d.title,
            description: d.description || '',
            tags: d.tags?.map((t: any) => ({ text: typeof t === 'string' ? t : t.text, variant: 'accent' as const })) || [],
            keywords: d.keywords || [],
            author_name: d.author_name || d.author?.nickname || '匿名',
            author_level: d.author_level || d.author?.rank || '',
            time: d.created_at ? new Date(d.created_at).toLocaleDateString() : '',
            download_count: d.download_count || 0,
            view_count: String(d.view_count || 0),
            like_count: d.like_count || 0,
            dislike_count: d.dislike_count || 0,
            price: d.price || 0,
            file_type: d.file_type || 'PDF',
            file_size: d.file_size || '',
          });
          setLiked(d.is_liked || false);
          setCollected(d.is_collected || false);
        }
      }).catch(() => {}).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [id]);

  const handleDownload = () => {
    if (isGuest) {
      checkAction('download');
      return;
    }
    setShowDownloadConfirm(true);
  };

  const confirmDownload = async () => {
    try {
      if (id) await resourceService.downloadResource(id);
      showToast('下载成功', 'success');
      setShowDownloadConfirm(false);
    } catch { showToast('下载失败', 'error'); }
  };

  const handleCollect = async () => {
    if (isGuest) {
      checkAction('collect');
      return;
    }
    try {
      if (id) {
        if (collected) {
          await resourceService.uncollectResource(id);
        } else {
          await resourceService.collectResource(id);
        }
      }
      setCollected(!collected);
      showToast(collected ? '已取消收藏' : '收藏成功', 'success');
    } catch {
      showToast('操作失败', 'error');
    }
  };

  const handleLike = async () => {
    if (isGuest) {
      checkAction('like');
      return;
    }
    try {
      if (id) await resourceService.likeResource(id);
      setLiked(!liked);
      showToast(liked ? '已取消点赞' : '点赞成功', 'success');
    } catch {
      showToast('操作失败', 'error');
    }
  };

  const handleReport = () => {
    if (isGuest) {
      checkAction('report');
      return;
    }
    setShowReport(true);
  };

  const submitReport = async () => {
    if (!reportReason) {
      showToast('请选择举报原因', 'error');
      return;
    }
    try {
      if (id) await resourceService.reportResource(id, { reason: reportReason, detail: reportDetail });
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
        <TopBar title="资源详情" />
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

          {resource.keywords.length > 0 && (
            <div className="tag-row" style={{ flexWrap: 'wrap', marginBottom: 'var(--spacing-xl)' }}>
              {resource.keywords.map((kw) => (
                <Tag key={kw} variant="accent">{kw}</Tag>
              ))}
            </div>
          )}

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
            <button className="icon-btn action-col" onClick={handleCollect}>
              {collected ? '⭐' : '☆'}<span>{collected ? '已收藏' : '收藏'}</span>
            </button>
            <button className="icon-btn action-col" onClick={handleLike}>
              👍<span>{resource.like_count + (liked ? 1 : 0)}</span>
            </button>
            <button className="icon-btn action-col" onClick={handleReport}>
              �<span>举报</span>
            </button>
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
            <span>{user?.cocoa_beans || 0} 🫘</span>
          </div>
          <button className="btn btn-primary btn-block btn-lg" onClick={confirmDownload}>确认下载</button>
          <button className="btn btn-secondary btn-block" style={{ marginTop: 'var(--spacing-sm)' }} onClick={() => setShowDownloadConfirm(false)}>取消</button>
        </div>
      </Modal>

      <Modal open={showReport} onClose={() => setShowReport(false)}>
        <div style={{ padding: 'var(--spacing-lg)' }}>
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 700, marginBottom: 'var(--spacing-lg)' }}>举报资源</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
            {REPORT_REASONS.map((reason) => (
              <label key={reason} style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="report-reason"
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

export default ResourceDetailPage;
