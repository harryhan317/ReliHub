import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { TopBar } from '../../layouts/Components';
import { resourceService } from '../../services/resourceService';

const categoryOptions = ['标准规范', '器件手册', '应用笔记', '工具模版', '案例分享', '培训资料', '推荐书单', '综合杂谈'];

const ResourceUploadPage: React.FC = () => {
  const navigate = useNavigate();
  const { isGuest } = useAuthStore();
  const { showToast } = useUIStore();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [keywords, setKeywords] = useState('');
  const [price, setPrice] = useState('5');
  const [fileName, setFileName] = useState('');

  const handleSubmit = async () => {
    if (isGuest) { showToast('请先登录', 'info'); navigate('/login'); return; }
    if (!fileName) { showToast('请上传文件', 'error'); return; }
    if (!title.trim()) { showToast('请输入资源标题', 'error'); return; }
    if (!category) { showToast('请选择分类', 'error'); return; }
    if (!description.trim() || description.trim().length < 10) { showToast('请输入至少10字的资源简介', 'error'); return; }
    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description);
      formData.append('category', category);
      formData.append('price', price);
      await resourceService.uploadResource(formData);
      showToast('资源上传成功，等待审核', 'success');
      navigate('/resource');
    } catch {
      showToast('上传失败', 'error');
    }
  };

  return (
    <div className="page active">
      <TopBar title="分享资源" />
      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-xl)' }}>
        <div className="upload-zone" onClick={() => setFileName('示例文件.pdf')}>
          {fileName ? (
            <div>
              <div style={{ fontSize: 36, marginBottom: 'var(--spacing-sm)' }}>📄</div>
              <div style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-secondary)' }}>{fileName}</div>
              <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)', marginTop: 4 }}>点击重新选择</div>
            </div>
          ) : (
            <div>
              <div style={{ fontSize: 36, marginBottom: 'var(--spacing-sm)' }}>📤</div>
              <div style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-secondary)' }}>点击或拖拽上传文件</div>
              <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-xs)' }}>支持 PDF/DOC/XLS/PPT/PNG/JPG，单文件≤20MB</div>
            </div>
          )}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-lg)' }}>
          <div className="input-group">
            <label className="input-label">资源标题<span className="required-mark">*</span></label>
            <input className="input-field" type="text" placeholder="请输入资源标题" maxLength={50} value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">资源分类<span className="required-mark">*</span></label>
            <select className="input-field" style={{ appearance: 'auto' }} value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">请选择分类</option>
              {categoryOptions.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          <div className="input-group">
            <label className="input-label">资源简介<span className="required-mark">*</span></label>
            <textarea className="input-field" rows={3} placeholder="请描述资源内容（10-500字）" style={{ resize: 'none' }} value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">关键词（最多5个）</label>
            <input className="input-field" type="text" placeholder="输入关键词，回车添加" value={keywords} onChange={(e) => setKeywords(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">下载所需可可豆</label>
            <input className="input-field" type="number" placeholder="5 ~ 100,000" value={price} min={5} max={100000} onChange={(e) => setPrice(e.target.value)} />
            <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)', marginTop: 2 }}>基础资源在用户权益额度内免费下载</div>
          </div>
          <button className="btn btn-primary btn-block btn-lg" onClick={handleSubmit}>提交审核</button>
        </div>
      </div>
    </div>
  );
};

export default ResourceUploadPage;
