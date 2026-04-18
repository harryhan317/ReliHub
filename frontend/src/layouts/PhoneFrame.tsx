import React from 'react';
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

const PhoneFrame: React.FC = () => {
  const { toasts } = useUIStore();
  const location = useLocation();

  return (
    <div className="phone-frame">
      <div className="phone-screen">
        <AnimatePresence mode="wait">
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
        </AnimatePresence>
        <ToastContainer toasts={toasts} />
      </div>
    </div>
  );
};

export default PhoneFrame;
