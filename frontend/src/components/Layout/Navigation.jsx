/**
 * Navigation Component
 * Purpose: Role-based navigation menu for OptiCare24
 * Reference: PROMPT.md → Role-Based Access Summary
 */

import { Navbar, Nav, Container, NavDropdown } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { getRoleDisplayName } from '../../utils/helpers';

const Navigation = () => {
  const { currentUser, userRole, logout } = useAuth();

  // Role-based navigation links
  const getNavLinks = () => {
    switch(userRole) {
      case 'admin':
        return (
          <>
            <Nav.Link as={Link} to="/dashboard">Dashboard</Nav.Link>
            <Nav.Link as={Link} to="/inventory">Inventory</Nav.Link>
            <Nav.Link as={Link} to="/customers">Customers</Nav.Link>
            <Nav.Link as={Link} to="/prescriptions">Prescriptions</Nav.Link>
            <Nav.Link as={Link} to="/orders">Orders</Nav.Link>
            <Nav.Link as={Link} to="/warranty">Warranty</Nav.Link>
            <Nav.Link as={Link} to="/appointments">Appointments</Nav.Link>
            <Nav.Link as={Link} to="/analytics">Analytics</Nav.Link>
          </>
        );
      case 'manager':
        return (
          <>
            <Nav.Link as={Link} to="/dashboard">Dashboard</Nav.Link>
            <Nav.Link as={Link} to="/inventory">Inventory</Nav.Link>
            <Nav.Link as={Link} to="/sales">Sales</Nav.Link>
            <Nav.Link as={Link} to="/discounts">Discounts</Nav.Link>
          </>
        );
      case 'staff':
        return (
          <>
            <Nav.Link as={Link} to="/dashboard">Dashboard</Nav.Link>
            <Nav.Link as={Link} to="/billing">Billing</Nav.Link>
            <Nav.Link as={Link} to="/customers">Customers</Nav.Link>
            <Nav.Link as={Link} to="/warranty">Warranty</Nav.Link>
          </>
        );
      case 'optometrist':
        return (
          <>
            <Nav.Link as={Link} to="/dashboard">Dashboard</Nav.Link>
            <Nav.Link as={Link} to="/prescriptions">Prescriptions</Nav.Link>
            <Nav.Link as={Link} to="/appointments">Appointments</Nav.Link>
          </>
        );
      case 'customer':
        return (
          <>
            <Nav.Link as={Link} to="/dashboard">Dashboard</Nav.Link>
            <Nav.Link as={Link} to="/orders">My Orders</Nav.Link>
            <Nav.Link as={Link} to="/prescriptions">My Prescriptions</Nav.Link>
            <Nav.Link as={Link} to="/appointments">Book Appointment</Nav.Link>
            <Nav.Link as={Link} to="/warranty">My Warranties</Nav.Link>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <Navbar bg="light" expand="lg" className="mb-3">
      <Container>
        <Navbar.Brand as={Link} to="/">
          OptiCare24
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            {currentUser ? getNavLinks() : (
              <>
                <Nav.Link as={Link} to="/">Home</Nav.Link>
                <Nav.Link as={Link} to="/about">About</Nav.Link>
                <Nav.Link as={Link} to="/contact">Contact</Nav.Link>
              </>
            )}
          </Nav>
          <Nav>
            {currentUser ? (
              <NavDropdown 
                title={`${currentUser.first_name || ''} (${getRoleDisplayName(userRole)})`} 
                id="user-dropdown"
              >
                <NavDropdown.Item as={Link} to="/profile">Profile</NavDropdown.Item>
                <NavDropdown.Divider />
                <NavDropdown.Item onClick={logout}>Logout</NavDropdown.Item>
              </NavDropdown>
            ) : (
              <>
                <Nav.Link as={Link} to="/login">Login</Nav.Link>
                <Nav.Link as={Link} to="/register">Register</Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation;