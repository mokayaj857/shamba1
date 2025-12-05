import React from 'react';
import { createRoot } from 'react-dom/client';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import HowItWorks from './components/HowItWorks';
import Landing from './components/Landing';
import Chatbot from './Pages/Chatbot';
import Layout from './components/Layout';
import LandDetails from './components/LandDetails';
import './index.css';
import { ToastProvider } from './components/toast/ToastProvider';

// Ensure i18n is initialized before rendering
i18n.init();

const router = createBrowserRouter([
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
  {
    path: '/how-it-works',
    element: <Layout showHeader><HowItWorks /></Layout>,
  },
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

// Create a root element
const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Failed to find the root element');
}

// Create a root
const root = createRoot(rootElement);

// Initial render
root.render(
  <React.StrictMode>
    <I18nextProvider i18n={i18n}>
      <ToastProvider>
        <RouterProvider router={router} />
      </ToastProvider>
    </I18nextProvider>
  </React.StrictMode>
);

// Enable React 18 concurrent features
if (import.meta.hot) {
  import.meta.hot.accept();
}