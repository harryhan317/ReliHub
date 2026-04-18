import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';

const MyTopicsPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const tabs = ['我发起的', '我回复的'];

  return (
    <div className="page active">
      <TopBar title="我的话题" />
      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={setActiveTab} />
      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-lg)' }}>
        <div className="empty-state">
          <div className="empty-state-icon">💬</div>
          <div className="empty-state-text">暂无话题，去社区参与讨论吧</div>
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/community')}>浏览社区</button>
        </div>
      </div>
    </div>
  );
};

export default MyTopicsPage;
