import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';

const MyResourcesPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const tabs = ['已上传', '已下载'];

  return (
    <div className="page active">
      <TopBar title="我的资源" />
      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={setActiveTab} />
      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-lg)' }}>
        <div className="empty-state">
          <div className="empty-state-icon">📚</div>
          <div className="empty-state-text">暂无资源，去分享你的第一个资源吧</div>
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/resource/upload')}>分享资源</button>
        </div>
      </div>
    </div>
  );
};

export default MyResourcesPage;
