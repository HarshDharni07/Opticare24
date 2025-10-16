/**
 * Layout Component
 * Purpose: Provides common layout structure with navigation based on user role
 * Reference: PROMPT.md → Role-Based Access section
 */

import { useAuth } from '../../context/AuthContext';
import { Container } from 'react-bootstrap';
import { Outlet } from 'react-router-dom';
import Navigation from './Navigation';
import Footer from './Footer';

const Layout = ({ children }) => {
  const { isAuthenticated, userRole } = useAuth();

  return (
    <div className="d-flex flex-column min-vh-100">
      <Navigation isAuthenticated={isAuthenticated} userRole={userRole} />
      
      <main className="flex-grow-1">
        <Container className="py-4">
          {children || <Outlet />}
        </Container>
      </main>
      
      <Footer />
    </div>
  );
};

export default Layout;