import React from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar } from '../../layouts/Components';

const MyCollectionsPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="page active">
      <TopBar title="我的收藏" />
      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-lg)' }}>
        <div className="empty-state">
          <div className="empty-state-icon">⭐</div>
          <div className="empty-state-text">暂无收藏内容</div>
        </div>
      </div>
    </div>
  );
};

export default MyCollectionsPage;
