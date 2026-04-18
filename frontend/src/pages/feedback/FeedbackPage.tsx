import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUIStore } from '../../store/uiStore';
import { TopBar, TabBar } from '../../layouts/Components';
import { feedbackService } from '../../services/otherServices';

const FeedbackPage: React.FC = () => {
  const navigate = useNavigate();
  const { showToast } = useUIStore();
  const [activeTab, setActiveTab] = useState(0);
  const [type, setType] = useState('');
  const [content, setContent] = useState('');
  const [contact, setContact] = useState('');

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
                <option value="功能建议">功能建议</option>
                <option value="Bug反馈">Bug反馈</option>
                <option value="内容投诉">内容投诉</option>
                <option value="其他">其他</option>
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
          <div className="empty-state">
            <div className="empty-state-icon">📝</div>
            <div className="empty-state-text">暂无反馈记录</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FeedbackPage;
