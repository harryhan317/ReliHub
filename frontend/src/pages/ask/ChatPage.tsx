import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { TopBar } from '../../layouts/Components';
import { Modal } from '../../components/ui/Modal';
import { aiService } from '../../services/aiService';

const ChatPage: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('query') || '';
  const { isLoggedIn } = useAuthStore();
  const { showToast } = useUIStore();

  const [messages, setMessages] = useState<Array<{
    role: 'user' | 'assistant';
    content: string;
    liked?: boolean;
    disliked?: boolean;
  }>>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(sessionId || '');
  const [showMore, setShowMore] = useState(false);
  const [showLimit, setShowLimit] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const sessionTitle = initialQuery ? initialQuery.substring(0, 10) : 'AI 对话';
  const currentRound = Math.ceil(messages.length / 2);
  const maxRounds = 10;
  const dailyUsed = 3;
  const dailyMax = 15;

  useEffect(() => {
    if (initialQuery) {
      handleSend(initialQuery);
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (text?: string) => {
    const content = text || inputValue.trim();
    if (!content) return;

    setMessages((prev) => [...prev, { role: 'user', content }]);
    setInputValue('');
    setIsTyping(true);

    try {
      if (currentSessionId) {
        const msgRes = await aiService.sendMessage(currentSessionId, content);
        if (msgRes.data) {
          setMessages((prev) => [...prev, { role: 'assistant', content: msgRes.data.content }]);
        }
      } else {
        await new Promise((r) => setTimeout(r, 1500));
        setMessages((prev) => [...prev, {
          role: 'assistant',
          content: `关于"${content}"的问题，这是可靠性工程领域的专业问题。\n\n根据可靠性工程标准，建议您从以下几个方面进行分析：\n\n1. **定义可靠性目标** — 确定产品在规定条件下的可靠性指标\n2. **失效模式分析** — 识别潜在的失效模式及影响\n3. **数据收集与分析** — 收集相关测试数据和现场数据\n4. **统计建模** — 选择合适的可靠性模型进行评估\n\n如需更详细的分析，请提供更多产品信息。`,
        }]);
      }
    } catch {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: '抱歉，我暂时无法回答这个问题，请稍后再试。',
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleLike = (index: number, type: 'like' | 'dislike') => {
    setMessages((prev) => prev.map((m, i) => {
      if (i === index && m.role === 'assistant') {
        return { ...m, liked: type === 'like' ? !m.liked : false, disliked: type === 'dislike' ? !m.disliked : false };
      }
      return m;
    }));
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentSessionId('');
    navigate('/chat');
  };

  const renderContent = (content: string) => {
    const parts = content.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={i} style={{ background: 'rgba(0,136,255,0.06)', padding: '2px 6px', borderRadius: 4, fontSize: '0.9em' }}>{part.slice(1, -1)}</code>;
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="page active">
      <div className="top-bar">
        <button className="top-bar-btn" onClick={() => navigate('/ask')}>←</button>
        <div className="top-bar-title" style={{ fontSize: 'var(--font-size-body)' }}>{sessionTitle}</div>
        <button className="top-bar-btn" onClick={() => setShowMore(true)}>✨</button>
      </div>

      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-lg)', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-lg)', paddingBottom: 80 }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', padding: 'var(--spacing-3xl) 0' }}>
            <div style={{ fontSize: 48, marginBottom: 'var(--spacing-lg)' }}>🤖</div>
            <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 600, marginBottom: 'var(--spacing-sm)' }}>ReliBot AI 助手</div>
            <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-tertiary)', lineHeight: 'var(--line-height-body)' }}>
              我是您的可靠性工程AI助手，可以回答技术问题、推导公式、提供方案建议
            </div>
          </div>
        )}

        <AnimatePresence>
          {messages.map((msg, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              style={{ display: 'flex', gap: 'var(--spacing-md)', alignItems: 'flex-start' }}
            >
              {msg.role === 'user' ? (
                <>
                  <div className="avatar" style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}>U</div>
                  <div style={{
                    flex: 1,
                    background: 'var(--color-bg-input)',
                    borderRadius: 'var(--radius-lg)',
                    padding: 'var(--spacing-md)',
                    fontSize: 'var(--font-size-body)',
                    lineHeight: 'var(--line-height-body)',
                  }}>
                    {msg.content}
                  </div>
                </>
              ) : (
                <>
                  <div className="avatar" style={{ background: 'linear-gradient(135deg, var(--color-accent-start), var(--color-accent-end))' }}>R</div>
                  <div style={{ flex: 1 }}>
                    <div className="ai-response-card">
                      {msg.content.split('\n').map((line, i) => (
                        <p key={i} style={{ marginTop: i > 0 ? 4 : 0 }}>{renderContent(line)}</p>
                      ))}
                    </div>
                    <div className="response-actions">
                      <button className="icon-btn" onClick={() => handleLike(index, 'like')}>👍</button>
                      <button className="icon-btn" onClick={() => handleLike(index, 'dislike')}>👎</button>
                      <button className="icon-btn" onClick={() => { navigator.clipboard.writeText(msg.content); showToast('已复制', 'success'); }}>📋</button>
                      <button className="icon-btn" onClick={() => showToast('链接已复制', 'success')}>🔗</button>
                    </div>
                  </div>
                </>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ display: 'flex', gap: 'var(--spacing-md)', alignItems: 'flex-start' }}
          >
            <div className="avatar" style={{ background: 'linear-gradient(135deg, var(--color-accent-start), var(--color-accent-end))' }}>R</div>
            <div className="ai-response-card">
              <div style={{ display: 'flex', gap: 4 }}>
                {[0, 1, 2].map((i) => (
                  <div key={i} style={{
                    width: 6, height: 6, borderRadius: '50%', background: 'var(--color-accent)',
                    animation: `typing 1.4s ease-in-out ${i * 0.2}s infinite`,
                  }} />
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {messages.length > 0 && (
          <div style={{ textAlign: 'center', fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)', padding: 'var(--spacing-sm)' }}>
            剩余 {maxRounds - currentRound}/{maxRounds} 轮 · 今日剩余 {dailyMax - dailyUsed}/{dailyMax} 轮
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-bar-no-nav" style={{ bottom: 'var(--safe-area-bottom)' }}>
        <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'center' }}>
          <button className="icon-btn" style={{ fontSize: 20 }}>📎</button>
          <input
            ref={inputRef}
            className="input-field"
            style={{ flex: 1, borderRadius: 'var(--radius-pill)', padding: '10px 16px' }}
            placeholder="继续提问..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !isTyping && handleSend()}
            disabled={isTyping}
          />
          <button className="btn btn-primary btn-sm" onClick={() => handleSend()} disabled={isTyping}>发送</button>
        </div>
      </div>

      <Modal open={showMore} onClose={() => setShowMore(false)}>
        <div style={{ padding: 'var(--spacing-lg)' }}>
          <div className="menu-item" onClick={() => { setShowMore(false); handleNewChat(); }}>
            <div className="menu-icon" style={{ background: 'var(--color-accent-light)' }}>➕</div>
            <span className="menu-text">新建对话</span>
          </div>
          <div className="menu-item" onClick={() => { setShowMore(false); navigate('/ask'); }}>
            <div className="menu-icon" style={{ background: 'var(--color-success-bg)' }}>📋</div>
            <span className="menu-text">历史对话</span>
          </div>
        </div>
      </Modal>

      <Modal open={showLimit} onClose={() => setShowLimit(false)}>
        <div style={{ padding: 'var(--spacing-lg)', textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 'var(--spacing-md)' }}>🤖</div>
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 600, marginBottom: 'var(--spacing-sm)' }}>今日对话次数已达上限</div>
          <div style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-tertiary)', marginBottom: 'var(--spacing-lg)', lineHeight: 'var(--line-height-body)' }}>
            注册用户每日可发起15轮AI对话，游客每日3轮。升级为注册用户可获得更多对话次数。
          </div>
          <button className="btn btn-primary btn-block btn-lg" onClick={() => { setShowLimit(false); navigate('/login'); }}>立即注册</button>
          <div style={{ marginTop: 'var(--spacing-md)', fontSize: 'var(--font-size-caption)', color: 'var(--color-text-muted)', cursor: 'pointer' }} onClick={() => setShowLimit(false)}>
            明天再来
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ChatPage;
