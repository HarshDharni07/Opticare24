/**
 * Application Root Component
 * Purpose: Initializes routing, layout, and authentication context for all roles.
 * Integrates React Router and Context API.
 * Reference: PROMPT.md → Frontend Global Architecture.
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import './App.css';

// Import context providers
import { AuthProvider } from './context/AuthContext';

// Import layout components
import Layout from './components/Layout/Layout';

// Import page components
import Home from './pages/Home';

function App() {
  return (
    <>
      <Router>
        <ToastContainer position="top-right" autoClose={3000} />
        <AuthProvider>
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              {/* More routes will be added here as components are developed */}
            </Routes>
          </Layout>
        </AuthProvider>
      </Router>
    </>
  );
}

export default App
