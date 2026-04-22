import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { useGuestGuard } from '../../store/useGuestGuard';
import { useGuestStore } from '../../store/guestStore';
import { BottomNav, GuestBanner, SearchBar, SectionHeader } from '../../layouts/Components';
import { Card, Tag } from '../../components/ui/Common';
import { Modal } from '../../components/ui/Modal';
import { GuestRegisterModal } from '../../components/ui/GuestRegisterModal';
import { aiService } from '../../services/aiService';

const AskPage: React.FC = () => {
  const navigate = useNavigate();
  const { isGuest, isLoggedIn } = useAuthStore();
  const { showToast } = useUIStore();
  const { checkAction, guideModal, closeGuideModal } = useGuestGuard();
  const guestStore = useGuestStore();
  const [inputValue, setInputValue] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [sessions, setSessions] = useState<Array<{ id: string; title: string; message_count: number; updated_at: string }>>([]);

  const suggestedQuestions = [
    '如何进行电子元器件的降额设计？',
    '温度循环试验的常见失效模式有哪些？',
  ];

  useEffect(() => {
    if (isLoggedIn) {
      aiService.getSessions(1, 10).then((res) => {
        if (res.data?.items) setSessions(res.data.items);
      }).catch(() => {});
    }
  }, [isLoggedIn]);

  const handleSend = () => {
    if (!inputValue.trim()) return;
    if (isGuest) {
      if (!checkAction('ai_limit')) return;
      guestStore.incrementAISession();
    }
    navigate(`/chat?query=${encodeURIComponent(inputValue)}`);
  };

  const handleSuggestedQuestion = (text: string) => {
    if (isGuest) {
      if (!checkAction('ai_limit')) return;
      guestStore.incrementAISession();
    }
    navigate(`/chat?query=${encodeURIComponent(text)}`);
  };

  return (
    <div className="page active">
      <div className="top-bar">
        <div className="top-bar-title gradient-text">ReliBot 爱问</div>
        <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
          <button className="top-bar-btn" onClick={() => { 
            if (isLoggedIn) { 
              aiService.getSessions(1, 20).then((res) => { 
                if (res.data?.items) {
                  setSessions(res.data.items);
                }
                setShowHistory(true);
              }).catch(() => {
                setShowHistory(true);
              }); 
            } else {
              setShowHistory(true);
            }
          }}>📋</button>
          <button className="top-bar-btn" onClick={() => navigate('/notification')} style={{ position: 'relative' }}>
            🔔
            <span style={{ position: 'absolute', top: 2, right: 2, width: 6, height: 6, background: 'var(--color-error)', borderRadius: '50%' }} />
          </button>
        </div>
      </div>

      {isGuest && (
        <GuestBanner text="游客模式 · 每日可发起3个AI对话" onAction={() => navigate('/login')} actionText="注册" />
      )}

      <SearchBar placeholder="搜索我的对话" onSearch={() => navigate('/search')} />

      <div className="content-area" style={{ padding: 'var(--spacing-md) var(--spacing-lg)' }}>
        <motion.div
          className="ai-intro-card"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 600, marginBottom: 'var(--spacing-sm)' }}>🤖 你好，我是 ReliBot</div>
          <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-tertiary)', lineHeight: 1.5 }}>
            我是电子产品可靠性领域的AI助手，可以帮你解答可靠性设计、测试、失效分析等专业问题。
          </div>
        </motion.div>

        <SectionHeader title="历史对话" action="查看全部" onAction={() => { 
          if (isLoggedIn) { 
            aiService.getSessions(1, 20).then((res) => { 
              if (res.data?.items) setSessions(res.data.items);
              setShowHistory(true);
            }).catch(() => {
              setShowHistory(true);
            }); 
          } else {
            setShowHistory(true);
          }
        }} />

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
          {sessions.length > 0 ? sessions.slice(0, 3).map((s, i) => (
            <motion.div
              key={s.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
            >
              <Card onClick={() => navigate(`/chat/${s.id}`)} style={{ cursor: 'pointer' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontWeight: 500 }}>{s.title || '未命名对话'}</div>
                  <Tag variant="accent">{s.message_count}条</Tag>
                </div>
                <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-tertiary)', marginTop: 'var(--spacing-xs)' }}>
                  {s.updated_at ? new Date(s.updated_at).toLocaleDateString('zh-CN') : ''}
                </div>
              </Card>
            </motion.div>
          )) : (
            <div style={{ textAlign: 'center', padding: 'var(--spacing-xl) 0', color: 'var(--color-text-muted)', fontSize: 'var(--font-size-caption)' }}>
              暂无历史对话，开始你的第一次提问吧
            </div>
          )}
        </div>

        <div style={{ marginTop: 'var(--spacing-xl)', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
          <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-xs)' }}>💡 试试问我：</div>
          {suggestedQuestions.map((q, i) => (
            <motion.div
              key={q}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.08 }}
            >
              <Card
                style={{ padding: 'var(--spacing-md)', cursor: 'pointer', borderStyle: 'dashed' }}
                onClick={() => handleSuggestedQuestion(q)}
              >
                <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-secondary)' }}>{q}</div>
              </Card>
            </motion.div>
          ))}
        </div>

        <div style={{ height: 80 }} />
      </div>

      <div className="chat-input-bar">
        <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'center' }}>
          <button className="icon-btn" style={{ fontSize: 20 }}>📎</button>
          <input
            className="input-field"
            style={{ flex: 1, borderRadius: 'var(--radius-pill)', padding: '10px 16px' }}
            placeholder="输入你的可靠性问题..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button className="btn btn-primary btn-sm" onClick={handleSend}>发送</button>
        </div>
      </div>

      <BottomNav activeTab="ask" />

      <Modal open={showHistory} onClose={() => setShowHistory(false)}>
        <div style={{ padding: 'var(--spacing-lg)' }}>
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 700, marginBottom: 'var(--spacing-lg)' }}>历史对话</div>
          {sessions.length > 0 ? sessions.map((s) => (
            <div key={s.id} className="history-item" onClick={() => { setShowHistory(false); navigate(`/chat/${s.id}`); }}>
              <div className="history-item-content">
                <div className="history-item-title">{s.title}</div>
                <div className="history-item-meta">{s.message_count} 条消息</div>
              </div>
              <span className="history-item-status" style={{ color: 'var(--color-accent)' }}>→</span>
            </div>
          )) : (
            <div className="empty-state">
              <div className="empty-state-icon">💬</div>
              <div className="empty-state-text">暂无历史对话</div>
            </div>
          )}
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

export default AskPage;
