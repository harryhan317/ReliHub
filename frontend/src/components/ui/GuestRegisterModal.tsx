import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useGuestStore } from '../../store/guestStore';

interface GuestRegisterModalProps {
  open: boolean;
  onClose: () => void;
  source: string;
  reason?: string;
}

const benefits = [
  { icon: '🤖', text: 'AI问答更多对话，专业解答可靠性问题' },
  { icon: '📚', text: '更多资源库访问，下载标准与案例' },
  { icon: '💬', text: '社区互动，与行业专家交流讨论' },
  { icon: '🫘', text: '注册即送30可可豆，早鸟额外20可可豆' },
];

export const GuestRegisterModal: React.FC<GuestRegisterModalProps> = ({ open, onClose, source, reason }) => {
  const navigate = useNavigate();
  const { markGuideShown } = useGuestStore();

  const handleRegister = (method: 'wechat' | 'phone') => {
    markGuideShown(source);
    const params = new URLSearchParams({
      source_scene: source,
      trigger_action: source,
      trigger_time: new Date().toISOString(),
    });
    navigate(`/login?${params.toString()}`);
  };

  const handleBack = () => {
    // 对于open_my动作，不记录时间，以便下次点击可以重新显示
    if (source !== 'open_my') {
      markGuideShown(source);
    }
    onClose();
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="modal-overlay active"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => {
              if (e.target === e.currentTarget) handleBack();
            }}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '38px' }}
          >
            <motion.div
              className="modal-content"
              style={{ maxHeight: '68%', maxWidth: '360px', borderRadius: 'var(--radius-xl)' }}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 0.85, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-handle" />
              <div style={{ padding: 'var(--spacing-xl)', display: 'flex', flexDirection: 'column', height: '100%' }}>
                <div style={{ textAlign: 'center', marginBottom: 'var(--spacing-md)', flexShrink: 0 }}>
                  <div style={{ fontSize: 36, marginBottom: 'var(--spacing-xs)' }}>✨</div>
                  <div style={{ fontSize: 'var(--font-size-h3)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                    注册解锁完整功能
                  </div>
                  {reason && (
                    <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-tertiary)' }}>
                      {reason}
                    </div>
                  )}
                </div>

                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', marginBottom: 'var(--spacing-sm)' }}>
                  <div className="register-guide-benefits" style={{ marginTop: '30px', marginBottom: 'var(--spacing-md)' }}>
                    {benefits.map((b, i) => (
                      <div key={i} className="benefit-item" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', padding: 'var(--spacing-xs) 0' }}>
                        <span className="benefit-icon">{b.icon}</span>
                        <span className="benefit-text">{b.text}</span>
                      </div>
                    ))}
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)', flexShrink: 0, marginTop: '25px' }}>
                    <button
                      className="btn btn-primary btn-md btn-block"
                      onClick={() => handleRegister('wechat')}
                      style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--spacing-sm)' }}
                    >
                      � 微信一键注册
                    </button>
                    <button
                      className="btn btn-secondary btn-md btn-block"
                      onClick={() => handleRegister('phone')}
                    >
                      📱 手机号注册
                    </button>
                    <button
                      className="btn btn-ghost btn-block"
                      onClick={handleBack}
                      style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-size-caption)' }}
                    >
                      返回继续浏览
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
