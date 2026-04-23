import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const WELCOME_LAST_VISIT_KEY = 'relihub_last_visit';
const WELCOME_HAS_SEEN_KEY = 'relihub_welcome_seen';

const WelcomePage: React.FC = () => {
  const navigate = useNavigate();
  const lastTapRef = useRef(0);
  const touchStartYRef = useRef(0);
  const [shouldShow, setShouldShow] = useState(false);
  const [displayDuration, setDisplayDuration] = useState(5000);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
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

    // 注释掉自动跳转逻辑，等待用户操作
    // timerRef.current = setTimeout(() => {
    //   handleProceed();
    // }, displayDuration);

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
        <div className="welcome-logo-wrapper">
          <div className="welcome-logo">R</div>
        </div>
        <div className="welcome-title gradient-text welcome-anim-text-1">ReliHub</div>
        <div className="welcome-product-code welcome-anim-text-2">ReliBot</div>
        <div className="welcome-subtitle welcome-anim-slogan">
          电子产品可靠性AI社区<br />专业 · 智能 · 共享
        </div>
        <div className="welcome-quote welcome-anim-slogan">"可靠性是设计出来的，不是测试出来的"</div>
        <button
          className="btn btn-primary btn-lg btn-block welcome-anim-fadein"
          onClick={(e) => { e.stopPropagation(); navigate('/login'); }}
        >
          欢迎注册/登录
        </button>
        <div
          className="welcome-skip welcome-anim-fadein"
          onClick={(e) => { e.stopPropagation(); handleProceed(); }}
        >
          路过，先来看看 →
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;
