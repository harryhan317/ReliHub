import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const WELCOME_LAST_VISIT_KEY = 'relihub_last_visit';
const WELCOME_HAS_SEEN_KEY = 'relihub_welcome_seen';

const WelcomePage: React.FC = () => {
  const navigate = useNavigate();
  const lastTapRef = useRef(0);
  const touchStartYRef = useRef(0);
  const [shouldShow, setShouldShow] = useState(false);
  const [displayDuration, setDisplayDuration] = useState(5000);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();
  const proceededRef = useRef(false);

  const handleProceed = useCallback(() => {
    if (proceededRef.current) return;
    proceededRef.current = true;
    if (timerRef.current) clearTimeout(timerRef.current);
    localStorage.setItem(WELCOME_LAST_VISIT_KEY, Date.now().toString());
    localStorage.setItem(WELCOME_HAS_SEEN_KEY, '1');
    navigate('/ask', { replace: true });
  }, [navigate]);

  useEffect(() => {
    const lastVisit = localStorage.getItem(WELCOME_LAST_VISIT_KEY);
    const hasSeen = localStorage.getItem(WELCOME_HAS_SEEN_KEY);

    if (!hasSeen) {
      setShouldShow(true);
      setDisplayDuration(5000);
    } else if (lastVisit) {
      const daysSince = (Date.now() - parseInt(lastVisit, 10)) / (1000 * 60 * 60 * 24);
      if (daysSince > 7) {
        setShouldShow(true);
        setDisplayDuration(3000);
      } else {
        navigate('/ask', { replace: true });
        return;
      }
    } else {
      setShouldShow(true);
      setDisplayDuration(5000);
    }
  }, [navigate]);

  useEffect(() => {
    if (!shouldShow) return;

    timerRef.current = setTimeout(() => {
      handleProceed();
    }, displayDuration);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [shouldShow, displayDuration, handleProceed]);

  const handleDoubleClick = () => {
    const now = Date.now();
    if (now - lastTapRef.current < 300) {
      handleProceed();
    }
    lastTapRef.current = now;
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartYRef.current = e.touches[0].clientY;
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    const deltaY = touchStartYRef.current - e.changedTouches[0].clientY;
    if (deltaY > 50) {
      handleProceed();
    }
  };

  if (!shouldShow) return null;

  return (
    <div
      className="page active"
      style={{ paddingTop: 'var(--safe-area-top)' }}
      onClick={handleDoubleClick}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
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
          onClick={(e) => { e.stopPropagation(); handleProceed(); }}
        >
          进入 ReliHub
        </button>
        <div
          className="welcome-skip"
          onClick={(e) => { e.stopPropagation(); handleProceed(); }}
        >
          跳过，随便看看 →
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;
