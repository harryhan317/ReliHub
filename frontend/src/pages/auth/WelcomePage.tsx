import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const WelcomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="page active" style={{ paddingTop: 'var(--safe-area-top)' }}>
      <div className="mesh-bg" />
      <div className="welcome-content">
        <motion.div
          className="welcome-logo"
          animate={{ y: [0, -6, 0] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        >
          R
        </motion.div>
        <div className="welcome-title gradient-text">ReliHub</div>
        <div className="welcome-subtitle">
          电子产品可靠性AI社区<br />专业 · 智能 · 共享
        </div>
        <div className="welcome-quote">"可靠性是设计出来的，不是测试出来的"</div>
        <button
          className="btn btn-primary btn-lg btn-block"
          onClick={() => navigate('/ask')}
        >
          进入 ReliHub
        </button>
        <div
          className="welcome-skip"
          onClick={() => navigate('/ask')}
        >
          跳过，随便看看 →
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;
