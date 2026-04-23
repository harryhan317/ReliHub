import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { useGuestGuard } from '../../store/useGuestGuard';
import { useGuestStore } from '../../store/guestStore';
import { Modal } from '../../components/ui/Modal';
import { GuestRegisterModal } from '../../components/ui/GuestRegisterModal';
import { aiService } from '../../services/aiService';

const MAX_INPUT_LENGTH = 2000;
const MAX_ROUNDS = 10;

interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  liked?: boolean;
  disliked?: boolean;
  timestamp?: string;
}

function renderMarkdown(text: string): React.ReactNode[] {
  const lines = text.split('\n');
  const result: React.ReactNode[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith('```')) {
      const lang = line.slice(3).trim();
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      result.push(
        <pre key={i} style={{
          background: 'rgba(0,0,0,0.04)',
          borderRadius: 8,
          padding: '12px 16px',
          overflowX: 'auto',
          margin: '8px 0',
          fontSize: '0.85em',
          lineHeight: 1.6,
        }}>
          {lang && <div style={{ fontSize: '0.8em', color: 'var(--color-text-muted)', marginBottom: 4 }}>{lang}</div>}
          <code>{codeLines.join('\n')}</code>
        </pre>
      );
      continue;
    }

    if (line.startsWith('### ')) {
      result.push(<h4 key={i} style={{ fontSize: '1em', fontWeight: 700, margin: '12px 0 4px' }}>{inlineFormat(line.slice(4))}</h4>);
      continue;
    }
    if (line.startsWith('## ')) {
      result.push(<h3 key={i} style={{ fontSize: '1.1em', fontWeight: 700, margin: '12px 0 4px' }}>{inlineFormat(line.slice(3))}</h3>);
      continue;
    }
    if (line.startsWith('# ')) {
      result.push(<h2 key={i} style={{ fontSize: '1.2em', fontWeight: 700, margin: '12px 0 4px' }}>{inlineFormat(line.slice(2))}</h2>);
      continue;
    }

    if (/^(\d+)\.\s/.test(line)) {
      const match = line.match(/^(\d+)\.\s(.*)$/);
      if (match) {
        result.push(
          <div key={i} style={{ display: 'flex', gap: 6, margin: '2px 0' }}>
            <span style={{ fontWeight: 700, color: 'var(--color-accent)', flexShrink: 0 }}>{match[1]}.</span>
            <span>{inlineFormat(match[2])}</span>
          </div>
        );
      }
      continue;
    }

    if (line.startsWith('- ') || line.startsWith('* ')) {
      result.push(
        <div key={i} style={{ display: 'flex', gap: 6, margin: '2px 0', paddingLeft: 8 }}>
          <span style={{ color: 'var(--color-accent)', flexShrink: 0 }}>•</span>
          <span>{inlineFormat(line.slice(2))}</span>
        </div>
      );
      continue;
    }

    if (line.startsWith('> ')) {
      result.push(
        <div key={i} style={{
          borderLeft: '3px solid var(--color-accent)',
          paddingLeft: 12,
          margin: '6px 0',
          color: 'var(--color-text-secondary)',
          fontStyle: 'italic',
        }}>
          {inlineFormat(line.slice(2))}
        </div>
      );
      continue;
    }

    if (line.trim() === '') {
      result.push(<div key={i} style={{ height: 6 }} />);
      continue;
    }

    result.push(<p key={i} style={{ margin: '2px 0' }}>{inlineFormat(line)}</p>);
  }

  return result;
}

function inlineFormat(text: string): React.ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[([^\]]+)\]\(([^)]+)\))/g);
  return parts.filter(Boolean).map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
      return <em key={i}>{part.slice(1, -1)}</em>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={i} style={{ background: 'rgba(0,136,255,0.06)', padding: '2px 6px', borderRadius: 4, fontSize: '0.9em' }}>{part.slice(1, -1)}</code>;
    }
    return <span key={i}>{part}</span>;
  });
}

const ChatPage: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('query') || '';
  const { isGuest, isLoggedIn } = useAuthStore();
  const { showToast } = useUIStore();
  const { checkAction, guideModal, closeGuideModal } = useGuestGuard();
  const guestStore = useGuestStore();

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [currentSessionId, setCurrentSessionId] = useState(sessionId || '');
  const [showMore, setShowMore] = useState(false);
  const [showNewChatConfirm, setShowNewChatConfirm] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [historySessions, setHistorySessions] = useState<Array<{ id: string; title: string; created_at: string }>>([]);
  const [charCount, setCharCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const initialQueryRef = useRef(initialQuery);

  const sessionTitle = messages.length > 0
    ? (messages[0].content.length > 10 ? messages[0].content.substring(0, 10) + '...' : messages[0].content)
    : 'AI 对话';
  const currentRound = Math.ceil(messages.filter(m => m.role === 'user').length);

  useEffect(() => {
    if (initialQueryRef.current && messages.length === 0) {
      handleSend(initialQueryRef.current);
      initialQueryRef.current = '';
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  const loadHistory = useCallback(async () => {
    try {
      const res = await aiService.getSessions(1, 20);
      if (res.data?.items) {
        setHistorySessions(res.data.items.map((s: any) => ({
          id: s.id,
          title: s.title || '未命名对话',
          created_at: s.created_at,
        })));
      }
    } catch {
      setHistorySessions([]);
    }
  }, []);

  const handleSend = async (text?: string) => {
    const content = (text || inputValue).trim();
    if (!content || isTyping) return;

    if (isGuest) {
      if (!checkAction('ai_limit')) return;
      guestStore.incrementAISession();
    }

    if (currentRound >= MAX_ROUNDS) {
      showToast(`单次对话最多${MAX_ROUNDS}轮，请新建对话`, 'info');
      return;
    }

    const userMsg: ChatMessage = { role: 'user', content, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setCharCount(0);
    setIsTyping(true);
    setStreamingContent('');

    try {
      let sid = currentSessionId;
      if (!sid) {
        const sessionRes = await aiService.createSession(content.substring(0, 30));
        sid = sessionRes.data?.id || '';
        setCurrentSessionId(sid);
      }

      abortRef.current = new AbortController();

      const streamUrl = aiService.getStreamUrl(sid);
      const response = await fetch(streamUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ content, session_id: sid }),
        signal: abortRef.current.signal,
      });

      if (response.ok && response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') break;
              try {
                const parsed = JSON.parse(data);
                if (parsed.content) {
                  fullContent += parsed.content;
                  setStreamingContent(fullContent);
                }
              } catch {
                fullContent += data;
                setStreamingContent(fullContent);
              }
            }
          }
        }

        setMessages((prev) => [...prev, {
          role: 'assistant',
          content: fullContent,
          timestamp: new Date().toISOString(),
        }]);
        setStreamingContent('');
      } else {
        const msgRes = await aiService.sendMessage(sid, content);
        if (msgRes.data) {
          setMessages((prev) => [...prev, {
            role: 'assistant',
            content: msgRes.data!.content,
            id: msgRes.data!.id,
            timestamp: msgRes.data!.created_at,
          }]);
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setMessages((prev) => [...prev, {
          role: 'assistant',
          content: '抱歉，我暂时无法回答这个问题，请稍后再试。',
          timestamp: new Date().toISOString(),
        }]);
      }
    } finally {
      setIsTyping(false);
      abortRef.current = null;
    }
  };

  const handleLike = async (index: number, type: 'like' | 'dislike') => {
    const msg = messages[index];
    if (msg.role !== 'assistant') return;

    setMessages((prev) => prev.map((m, i) => {
      if (i === index) {
        return { ...m, liked: type === 'like' ? !m.liked : false, disliked: type === 'dislike' ? !m.disliked : false };
      }
      return m;
    }));

    if (msg.id) {
      try {
        if (type === 'like') await aiService.likeMessage(sessionId, msg.id);
        else await aiService.dislikeMessage(sessionId, msg.id);
      } catch { /* silent */ }
    }
  };

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content);
    showToast('已复制到剪贴板', 'success');
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({ title: 'ReliHub AI对话', text: messages.map(m => `${m.role === 'user' ? '我' : 'AI'}: ${m.content}`).join('\n\n') });
    } else {
      navigator.clipboard.writeText(messages.map(m => `${m.role === 'user' ? '我' : 'AI'}: ${m.content}`).join('\n\n'));
      showToast('对话内容已复制', 'success');
    }
  };

  const handleDeleteSession = async () => {
    if (currentSessionId) {
      try {
        await aiService.deleteSession(currentSessionId);
      } catch { /* silent */ }
    }
    setMessages([]);
    setCurrentSessionId('');
    setShowMore(false);
    showToast('对话已删除', 'success');
  };

  const handleNewChat = () => {
    if (messages.length > 0 && !currentSessionId) {
      setShowNewChatConfirm(true);
      return;
    }
    setMessages([]);
    setCurrentSessionId('');
    navigate('/chat', { replace: true });
  };

  const handleContinueSession = async (sid: string) => {
    try {
      const sessionRes = await aiService.getSession(sid);
      if (sessionRes.data) {
        setCurrentSessionId(sid);
        const msgRes = await aiService.getMessages(sid);
        if (msgRes.data?.items) {
          setMessages(msgRes.data.items.map((m: any) => ({
            id: m.id,
            role: m.role,
            content: m.content,
            timestamp: m.created_at,
          })));
        }
        setShowHistory(false);
        navigate(`/chat/${sid}`, { replace: true });
      }
    } catch {
      showToast('加载对话失败', 'error');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    if (val.length <= MAX_INPUT_LENGTH) {
      setInputValue(val);
      setCharCount(val.length);
    }
  };

  return (
    <div className="page active">
      <div className="top-bar">
        <button className="top-bar-btn" onClick={() => navigate('/ask')}>←</button>
        <div className="top-bar-title" style={{ fontSize: 'var(--font-size-body)' }}>{sessionTitle}</div>
        <button className="top-bar-btn" onClick={() => setShowMore(true)}>✨</button>
      </div>

      <div className="content-area-no-nav" style={{ padding: 'var(--spacing-lg)', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-lg)', paddingBottom: 80 }}>
        {messages.length === 0 && !isTyping && (
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
                      {renderMarkdown(msg.content)}
                    </div>
                    <div className="response-actions">
                      <button
                        className={`icon-btn ${msg.liked ? 'active' : ''}`}
                        onClick={() => handleLike(index, 'like')}
                        style={msg.liked ? { background: 'var(--color-accent-light)', borderRadius: 'var(--radius-sm)' } : {}}
                      >
                        👍
                      </button>
                      <button
                        className={`icon-btn ${msg.disliked ? 'active' : ''}`}
                        onClick={() => handleLike(index, 'dislike')}
                        style={msg.disliked ? { background: 'rgba(239,68,68,0.1)', borderRadius: 'var(--radius-sm)' } : {}}
                      >
                        👎
                      </button>
                      <button className="icon-btn" onClick={() => handleCopy(msg.content)}>📋</button>
                      <button className="icon-btn" onClick={handleShare}>🔗</button>
                    </div>
                  </div>
                </>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {isTyping && streamingContent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ display: 'flex', gap: 'var(--spacing-md)', alignItems: 'flex-start' }}
          >
            <div className="avatar" style={{ background: 'linear-gradient(135deg, var(--color-accent-start), var(--color-accent-end))' }}>R</div>
            <div style={{ flex: 1 }}>
              <div className="ai-response-card">
                {renderMarkdown(streamingContent)}
                <span className="cursor-blink" style={{ display: 'inline-block', width: 2, height: 16, background: 'var(--color-accent)', marginLeft: 2, verticalAlign: 'text-bottom', animation: 'blink 1s step-end infinite' }} />
              </div>
            </div>
          </motion.div>
        )}

        {isTyping && !streamingContent && (
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
            剩余 {MAX_ROUNDS - currentRound}/{MAX_ROUNDS} 轮
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-bar-no-nav" style={{ bottom: 'var(--safe-area-bottom)' }}>
        <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'center' }}>
          <button className="icon-btn" style={{ fontSize: 20 }} onClick={() => setShowHistory(true)}>📋</button>
          <div style={{ flex: 1, position: 'relative' }}>
            <input
              ref={inputRef}
              className="input-field"
              style={{ width: '100%', borderRadius: 'var(--radius-pill)', padding: '10px 16px', paddingRight: 50 }}
              placeholder="继续提问..."
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={(e) => e.key === 'Enter' && !isTyping && handleSend()}
              disabled={isTyping}
              maxLength={MAX_INPUT_LENGTH}
            />
            {charCount > MAX_INPUT_LENGTH * 0.8 && (
              <span style={{
                position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                fontSize: 'var(--font-size-small)',
                color: charCount >= MAX_INPUT_LENGTH ? 'var(--color-error)' : 'var(--color-text-muted)',
              }}>
                {charCount}/{MAX_INPUT_LENGTH}
              </span>
            )}
          </div>
          <button className="btn btn-primary btn-sm" onClick={() => handleSend()} disabled={isTyping || !inputValue.trim()}>发送</button>
        </div>
      </div>

      <Modal open={showMore} onClose={() => setShowMore(false)}>
        <div style={{ padding: 'var(--spacing-lg)' }}>
          <div className="menu-item" onClick={() => { setShowMore(false); handleNewChat(); }}>
            <div className="menu-icon" style={{ background: 'var(--color-accent-light)' }}>➕</div>
            <span className="menu-text">新建对话</span>
          </div>
          <div className="menu-item" onClick={() => { setShowMore(false); loadHistory().then(() => setShowHistory(true)); }}>
            <div className="menu-icon" style={{ background: 'var(--color-success-bg)' }}>📋</div>
            <span className="menu-text">历史对话</span>
          </div>
          <div className="menu-item" onClick={handleShare}>
            <div className="menu-icon" style={{ background: 'rgba(59,130,246,0.1)' }}>🔗</div>
            <span className="menu-text">分享对话</span>
          </div>
          <div className="menu-item" onClick={handleDeleteSession} style={{ color: 'var(--color-error)' }}>
            <div className="menu-icon" style={{ background: 'rgba(239,68,68,0.1)' }}>🗑️</div>
            <span className="menu-text" style={{ color: 'var(--color-error)' }}>删除对话</span>
          </div>
        </div>
      </Modal>

      <Modal open={showNewChatConfirm} onClose={() => setShowNewChatConfirm(false)}>
        <div style={{ padding: 'var(--spacing-xl)', textAlign: 'center' }}>
          <div style={{ fontSize: 36, marginBottom: 'var(--spacing-md)' }}>⚠️</div>
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 700, marginBottom: 'var(--spacing-sm)' }}>确认新建对话？</div>
          <div style={{ fontSize: 'var(--font-size-body)', color: 'var(--color-text-tertiary)', marginBottom: 'var(--spacing-lg)' }}>
            当前对话内容将不会被保存，确认要新建对话吗？
          </div>
          <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
            <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setShowNewChatConfirm(false)}>取消</button>
            <button className="btn btn-primary" style={{ flex: 1 }} onClick={() => {
              setShowNewChatConfirm(false);
              setMessages([]);
              setCurrentSessionId('');
              navigate('/chat', { replace: true });
            }}>确认</button>
          </div>
        </div>
      </Modal>

      <Modal open={showHistory} onClose={() => setShowHistory(false)}>
        <div style={{ padding: 'var(--spacing-lg)' }}>
          <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 700, marginBottom: 'var(--spacing-lg)' }}>历史对话</div>
          {historySessions.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)', color: 'var(--color-text-muted)' }}>
              暂无历史对话
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)', maxHeight: '50vh', overflowY: 'auto' }}>
              {historySessions.map((session) => (
                <div
                  key={session.id}
                  className="menu-item"
                  onClick={() => handleContinueSession(session.id)}
                  style={{ borderRadius: 'var(--radius-md)' }}
                >
                  <div className="menu-icon" style={{ background: 'var(--color-accent-light)' }}>💬</div>
                  <div style={{ flex: 1 }}>
                    <div className="menu-text">{session.title}</div>
                    <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-muted)' }}>
                      {new Date(session.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
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

export default ChatPage;
