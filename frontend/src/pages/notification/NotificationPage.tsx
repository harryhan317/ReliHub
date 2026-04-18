import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';
import { notificationService } from '../../services/otherServices';

interface NotifItem {
  id: string;
  title: string;
  desc: string;
  time: string;
  unread: boolean;
}

const systemNotifs: NotifItem[] = [
  { id: 's1', title: '🎉 欢迎加入 ReliHub', desc: '注册成功！完成个人档案可获得额外可可豆奖励', time: '刚刚', unread: true },
  { id: 's2', title: '🏆 早鸟奖励到账', desc: '恭喜获得20可可豆早鸟奖励，快去使用吧！', time: '1分钟前', unread: true },
  { id: 's3', title: '📢 系统公告', desc: 'ReliHub MVP版本正式上线，欢迎体验并提出宝贵意见', time: '1小时前', unread: false },
];

const interactNotifs: NotifItem[] = [
  { id: 'i1', title: '👍 王专家赞了你的回复', desc: '在话题"BGA焊点开裂"中', time: '3小时前', unread: false },
  { id: 'i2', title: '💬 陈工回复了你的话题', desc: '关于加速寿命试验方案的问题，建议使用Arrhenius模型...', time: '5小时前', unread: false },
  { id: 'i3', title: '⭐ 张工收藏了你的资源', desc: '"GJB/Z 299C 可靠性预计手册"', time: '昨天', unread: false },
];

const serviceNotifs: NotifItem[] = [
  { id: 'v1', title: '📥 资源审核通过', desc: '你上传的"降额设计速查表"已通过审核', time: '2天前', unread: false },
  { id: 'v2', title: '✅ 回复被采纳', desc: '你在"ESD防护方案"中的回复被采纳为最佳回答，获得50可可豆', time: '3天前', unread: false },
];

const NotificationPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const tabs = ['系统', '互动', '服务'];

  const allNotifs = [systemNotifs, interactNotifs, serviceNotifs];
  const currentNotifs = allNotifs[activeTab] || [];

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markAllRead();
    } catch {}
  };

  return (
    <div className="page active">
      <TopBar title="消息通知" rightContent={
        <button className="top-bar-btn" onClick={handleMarkAllRead} style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-accent)', width: 'auto' }}>全部已读</button>
      } />
      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={setActiveTab} />
      <div className="content-area-no-nav">
        {currentNotifs.length > 0 ? currentNotifs.map((notif) => (
          <div key={notif.id} className={`notif-item ${notif.unread ? 'unread' : ''}`}>
            <div className={`notif-dot ${notif.unread ? '' : 'read'}`}></div>
            <div className="notif-content">
              <div className="notif-title">{notif.title}</div>
              <div className="notif-desc">{notif.desc}</div>
            </div>
            <div className="notif-time">{notif.time}</div>
          </div>
        )) : (
          <div className="empty-state">
            <div className="empty-state-icon">🔔</div>
            <div className="empty-state-text">暂无通知</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationPage;
