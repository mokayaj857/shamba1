import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import HowItWorks from './components/HowItWorks';
import Landing from './components/Landing';
import Chatbot from './Pages/Chatbot.tsx';

import Layout from './components/Layout';


import LandDetails from './components/LandDetails';

import './index.css';
import { ToastProvider } from './components/toast/ToastProvider';

;

const router = createBrowserRouter([
  // Landing page with clear value proposition
  {
    path: '/',
    element: <Layout showHeader><Landing /></Layout>,
  },
 
  
  
  
  {
    path: '/chat',
    element: <Layout showHeader><Chatbot /></Layout>,
  },
  {
    path: '/land',
    element: <Layout showHeader><LandDetails /></Layout>,
    
  },
  // How it works
  {
    path: '/how-it-works',
    element: <Layout showHeader><HowItWorks /></Layout>,
  },
  // Legacy routes for backward compatibility
  {
    path: '/trusted',
    element: <Navigate to="/inspectors" replace />,
  },
  
  
  {
    path: '/discover',
    element: <Navigate to="/how-it-works" replace />,
  },
  {
    path: '/chatbot',
    element: <Layout showHeader><Chatbot /></Layout>,
  },
  
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element not found");
}
ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <I18nextProvider i18n={i18n}>
      <ToastProvider>
        <RouterProvider router={router} />
      </ToastProvider>
    </I18nextProvider>
  </React.StrictMode>
);