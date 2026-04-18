import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { TopBar } from '../../layouts/Components';
import { communityService } from '../../services/communityService';

const categoryOptions = ['可靠性设计', '信号测试', '环境实验', '元器件', '失效分析', '标准解读', '质量管理', '工艺可靠性', '行业动态', '综合问答'];

const NewTopicPage: React.FC = () => {
  const navigate = useNavigate();
  const { isGuest } = useAuthStore();
  const { showToast } = useUIStore();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('');
  const [bounty, setBounty] = useState('');
  const [agreed, setAgreed] = useState(false);

  const handleSubmit = async () => {
    if (isGuest) { showToast('请先登录', 'info'); navigate('/login'); return; }
    if (!title.trim() || title.trim().length < 5) { showToast('标题至少5个字', 'error'); return; }
    if (!category) { showToast('请选择分类', 'error'); return; }
    if (!content.trim() || content.trim().length < 10) { showToast('内容至少10个字', 'error'); return; }
    if (!agreed) { showToast('请阅读并同意社区发帖规范', 'error'); return; }
    try {
      await communityService.createTopic({
        title, content, category,
        bounty: parseInt(bounty) || 0,
      });
      showToast('发布成功', 'success');
      navigate('/community');
    } catch {
      showToast('发布失败', 'error');
    }
  };

  return (
    <div className="page active">
      <TopBar title="发起新话题" rightContent={
        <button className="top-bar-btn" onClick={handleSubmit} style={{ color: 'var(--color-accent)', fontWeight: 600, fontSize: 'var(--font-size-body)' }}>发布</button>
      } />
      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-xl)' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-lg)' }}>
          <div className="input-group">
            <label className="input-label">标题<span className="required-mark">*</span></label>
            <input className="input-field" type="text" placeholder="请输入话题标题（5-100字）" maxLength={100} value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">分类<span className="required-mark">*</span></label>
            <select className="input-field" style={{ appearance: 'auto' }} value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">请选择分类</option>
              {categoryOptions.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          <div className="input-group">
            <label className="input-label">内容<span className="required-mark">*</span></label>
            <textarea className="input-field" rows={6} placeholder="详细描述你的问题或观点（10-2000字）" style={{ resize: 'none' }} value={content} onChange={(e) => setContent(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">上传附件（可选）</label>
            <div className="upload-zone" style={{ padding: 'var(--spacing-xl)', marginBottom: 0 }}>
              <div style={{ fontSize: 24 }}>📎</div>
              <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)', marginTop: 4 }}>添加图片/文件</div>
            </div>
          </div>
          <div className="input-group">
            <label className="input-label">设置悬赏（可选）</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
              <input className="input-field" type="number" placeholder="0" min={0} style={{ width: 100 }} value={bounty} onChange={(e) => setBounty(e.target.value)} />
              <span style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-tertiary)' }}>🫘 可可豆</span>
            </div>
            <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)', marginTop: 4 }}>悬赏将激励更多专业人士参与讨论</div>
          </div>
          <div className="agreement-row">
            <div className="checkbox-wrapper" onClick={() => setAgreed(!agreed)}>
              <div className={`checkbox ${agreed ? 'checked' : ''}`} />
            </div>
            <span>我已阅读并同意 <a href="#" style={{ color: 'var(--color-accent)' }}>《社区发帖规范》</a></span>
          </div>
          <button className="btn btn-primary btn-block btn-lg" onClick={handleSubmit}>发布话题</button>
        </div>
      </div>
    </div>
  );
};

export default NewTopicPage;
