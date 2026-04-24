import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUIStore } from '../../store/uiStore';
import { TopBar, TabBar } from '../../layouts/Components';
import { feedbackService } from '../../services/otherServices';

interface FeedbackItem {
  id: string;
  type: string;
  content: string;
  status: string;
  created_at: string;
}

const FeedbackPage: React.FC = () => {
  const navigate = useNavigate();
  const { showToast } = useUIStore();
  const [activeTab, setActiveTab] = useState(0);
  const [type, setType] = useState('');
  const [content, setContent] = useState('');
  const [contact, setContact] = useState('');
  const [history, setHistory] = useState<FeedbackItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 1) {
      setHistoryLoading(true);
      feedbackService.getFeedbackHistory({ page: 1, page_size: 20 }).then((res) => {
        if (res.data?.items) {
          setHistory(res.data.items.map((f: any) => ({
            id: f.id,
            type: f.type || '',
            content: f.content || '',
            status: f.status || 'pending',
            created_at: f.created_at || '',
          })));
        }
      }).catch(() => {}).finally(() => setHistoryLoading(false));
    }
  }, [activeTab]);

  const handleSubmit = async () => {
    if (!type) { showToast('请选择反馈类型', 'error'); return; }
    if (!content.trim() || content.trim().length < 10) { showToast('请输入至少10字的反馈内容', 'error'); return; }
    try {
      await feedbackService.createFeedback({ type, content, contact: contact || undefined });
      showToast('感谢您的反馈！', 'success');
      navigate(-1);
    } catch {
      showToast('提交失败', 'error');
    }
  };

  return (
    <div className="page active">
      <TopBar title="意见反馈" />
      <TabBar tabs={['提交反馈', '反馈历史']} activeIndex={activeTab} onTabChange={setActiveTab} />
      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-xl)' }}>
        {activeTab === 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-lg)' }}>
            <div className="input-group">
              <label className="input-label">反馈类型<span className="required-mark">*</span></label>
              <select className="input-field" style={{ appearance: 'auto' }} value={type} onChange={(e) => setType(e.target.value)}>
                <option value="">请选择类型</option>
                <option value="BUG">功能异常</option>
                <option value="SUGGESTION">体验建议</option>
                <option value="CONTENT">内容纠错</option>
                <option value="OTHER">其他</option>
              </select>
            </div>
            <div className="input-group">
              <label className="input-label">详细描述<span className="required-mark">*</span></label>
              <textarea
                className="input-field"
                rows={5}
                placeholder="请详细描述你的问题或建议（10-1000字）"
                style={{ resize: 'none' }}
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />
            </div>
            <div className="input-group">
              <label className="input-label">上传截图（可选）</label>
              <div className="upload-zone" style={{ padding: 'var(--spacing-xl)', marginBottom: 0 }}>
                <div style={{ fontSize: 24 }}>📷</div>
                <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)', marginTop: 4 }}>添加截图</div>
              </div>
            </div>
            <div className="input-group">
              <label className="input-label">联系方式（可选）</label>
              <input className="input-field" type="text" placeholder="手机号或邮箱，方便我们联系你" value={contact} onChange={(e) => setContact(e.target.value)} />
            </div>
            <button className="btn btn-primary btn-block btn-lg" onClick={handleSubmit}>提交反馈</button>
          </div>
        ) : (
          historyLoading ? (
            <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)', color: 'var(--color-text-muted)' }}>
              <div style={{ fontSize: 32, marginBottom: 8 }}>⏳</div>
              <div>加载中...</div>
            </div>
          ) : history.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              {history.map((item) => (
                <div key={item.id} style={{ padding: 'var(--spacing-md)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-lg)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-xs)' }}>
                    <span style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-accent)', fontWeight: 600 }}>{item.type}</span>
                    <span style={{ fontSize: 'var(--font-size-small)', color: item.status === 'resolved' ? 'var(--color-success)' : 'var(--color-warning)' }}>
                      {item.status === 'resolved' ? '已处理' : '处理中'}
                    </span>
                  </div>
                  <div style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-primary)', lineHeight: 'var(--line-height-body)' }}>
                    {item.content.substring(0, 100)}{item.content.length > 100 ? '...' : ''}
                  </div>
                  {item.created_at && (
                    <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-xs)' }}>
                      {new Date(item.created_at).toLocaleDateString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">📝</div>
              <div className="empty-state-text">暂无反馈记录</div>
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default FeedbackPage;
