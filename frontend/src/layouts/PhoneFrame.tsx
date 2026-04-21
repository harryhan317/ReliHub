import React, { useEffect, useRef } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { ToastContainer } from '../components/ui/Modal';
import { useUIStore } from '../store/uiStore';

const pageVariants = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
};

const pageTransition = {
  type: 'tween' as const,
  ease: 'easeInOut' as const,
  duration: 0.25,
};

const ScrollToTop: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const prevPathname = useRef(location.pathname);

  useEffect(() => {
    if (location.pathname !== prevPathname.current) {
      prevPathname.current = location.pathname;
      const pageEl = document.querySelector('.page.active');
      if (pageEl) {
        pageEl.scrollTop = 0;
      }
      const contentArea = pageEl?.querySelector('.content-area, .content-area-no-nav');
      if (contentArea) {
        contentArea.scrollTop = 0;
      }
    }
  }, [location.pathname]);

  return <>{children}</>;
};

const PhoneFrame: React.FC = () => {
  const { toasts } = useUIStore();
  const location = useLocation();

  return (
    <div className="phone-frame">
      <div className="phone-screen">
        <AnimatePresence mode="wait">
          <ScrollToTop>
            <motion.div
              key={location.pathname}
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={pageTransition}
              style={{ width: '100%', height: '100%' }}
            >
              <Outlet />
            </motion.div>
          </ScrollToTop>
        </AnimatePresence>
        <ToastContainer toasts={toasts} />
      </div>
    </div>
  );
};

export default PhoneFrame;
