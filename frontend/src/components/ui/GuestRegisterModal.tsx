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
  { icon: '🤖', text: 'AI问答无限对话，专业解答可靠性问题' },
  { icon: '📚', text: '完整资源库访问，下载标准与案例' },
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
    markGuideShown(source);
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
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <motion.div
              className="modal-content"
              style={{ maxHeight: '80%', borderRadius: 'var(--radius-xl)' }}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-handle" />
              <div style={{ padding: 'var(--spacing-xl)' }}>
                <div style={{ textAlign: 'center', marginBottom: 'var(--spacing-lg)' }}>
                  <div style={{ fontSize: 40, marginBottom: 'var(--spacing-sm)' }}>✨</div>
                  <div style={{ fontSize: 'var(--font-size-h2)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                    注册解锁完整功能
                  </div>
                  {reason && (
                    <div style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-tertiary)' }}>
                      {reason}
                    </div>
                  )}
                </div>

                <div className="register-guide-benefits">
                  {benefits.map((b, i) => (
                    <div key={i} className="benefit-item">
                      <span className="benefit-icon">{b.icon}</span>
                      <span className="benefit-text">{b.text}</span>
                    </div>
                  ))}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                  <button
                    className="btn btn-primary btn-lg btn-block"
                    onClick={() => handleRegister('wechat')}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--spacing-sm)' }}
                  >
                    💚 微信一键注册
                  </button>
                  <button
                    className="btn btn-secondary btn-lg btn-block"
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
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
