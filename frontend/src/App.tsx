import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { router } from './router';
import './assets/styles/design-system.css';
import './assets/styles/components.css';
import './assets/styles/pages.css';

const App: React.FC = () => {
  return <RouterProvider router={router} />;
};

export default App;
