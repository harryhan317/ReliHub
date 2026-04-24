import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar, TabBar } from '../../layouts/Components';
import { notificationService } from '../../services/otherServices';

interface NotifItem {
  id: string;
  title: string;
  desc: string;
  time: string;
  unread: boolean;
  type: string;
  ref_id?: string;
}

const NotificationPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [systemNotifs, setSystemNotifs] = useState<NotifItem[]>([]);
  const [interactNotifs, setInteractNotifs] = useState<NotifItem[]>([]);
  const [serviceNotifs, setServiceNotifs] = useState<NotifItem[]>([]);
  const [loading, setLoading] = useState(true);
  const tabs = ['系统', '互动', '服务'];

  const loadNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const res = await notificationService.getNotifications({});
      if (res.data?.items) {
        const mapped = res.data.items.map((n: any) => ({
          id: n.id,
          title: n.title || '',
          desc: n.content || n.desc || '',
          time: n.created_at ? formatTime(n.created_at) : '',
          unread: !n.is_read,
          type: n.type || n.category || 'system',
          ref_id: n.ref_id || n.reference_id,
        }));
        setSystemNotifs(mapped.filter((n: NotifItem) => n.type === 'system'));
        setInteractNotifs(mapped.filter((n: NotifItem) => n.type === 'interaction' || n.type === 'interact'));
        setServiceNotifs(mapped.filter((n: NotifItem) => n.type === 'service'));
      }
    } catch {
      setSystemNotifs([
        { id: 's1', title: '🎉 欢迎加入 ReliHub', desc: '注册成功！完成个人档案可获得额外可可豆奖励', time: '刚刚', unread: true, type: 'system' },
        { id: 's2', title: '🏆 早鸟奖励到账', desc: '恭喜获得20可可豆早鸟奖励，快去使用吧！', time: '1分钟前', unread: true, type: 'system' },
      ]);
      setInteractNotifs([
        { id: 'i1', title: '👍 王专家赞了你的回复', desc: '在话题"BGA焊点开裂"中', time: '3小时前', unread: false, type: 'interaction' },
        { id: 'i2', title: '💬 陈工回复了你的话题', desc: '关于加速寿命试验方案的问题', time: '5小时前', unread: false, type: 'interaction' },
      ]);
      setServiceNotifs([
        { id: 'v1', title: '📥 资源审核通过', desc: '你上传的"降额设计速查表"已通过审核', time: '2天前', unread: false, type: 'service' },
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadNotifications();
  }, [loadNotifications]);

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}小时前`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}天前`;
    return date.toLocaleDateString();
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markAllRead();
    } catch {}
    const markRead = (items: NotifItem[]) => items.map((n) => ({ ...n, unread: false }));
    setSystemNotifs(markRead);
    setInteractNotifs(markRead);
    setServiceNotifs(markRead);
  };

  const handleNotifClick = async (notif: NotifItem) => {
    if (notif.unread) {
      try { await notificationService.markRead(notif.id); } catch {}
      const markOneRead = (items: NotifItem[]) => items.map((n) => n.id === notif.id ? { ...n, unread: false } : n);
      setSystemNotifs(markOneRead);
      setInteractNotifs(markOneRead);
      setServiceNotifs(markOneRead);
    }
    if (notif.ref_id) {
      if (notif.type === 'interaction') navigate(`/community/topic/${notif.ref_id}`);
      else if (notif.type === 'service' && notif.title.includes('资源')) navigate(`/resource/${notif.ref_id}`);
    }
  };

  const allNotifs = [systemNotifs, interactNotifs, serviceNotifs];
  const currentNotifs = allNotifs[activeTab] || [];
  const unreadCount = currentNotifs.filter((n) => n.unread).length;

  return (
    <div className="page active">
      <TopBar title="消息通知" rightContent={
        <button className="top-bar-btn" onClick={handleMarkAllRead} style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-accent)', width: 'auto' }}>
          全部已读{unreadCount > 0 ? `(${unreadCount})` : ''}
        </button>
      } />
      <TabBar tabs={tabs} activeIndex={activeTab} onTabChange={setActiveTab} />
      <div className="content-area-no-nav">
        {loading ? (
          <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)', color: 'var(--color-text-muted)' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>⏳</div>
            <div>加载中...</div>
          </div>
        ) : currentNotifs.length > 0 ? currentNotifs.map((notif) => (
          <div key={notif.id} className={`notif-item ${notif.unread ? 'unread' : ''}`} style={{ cursor: notif.ref_id ? 'pointer' : 'default' }} onClick={() => handleNotifClick(notif)}>
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
