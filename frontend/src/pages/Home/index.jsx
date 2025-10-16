/**
 * Home Page Component
 * Purpose: Landing page for non-authenticated users
 * Reference: PROMPT.md → Frontend structure
 */

import { Container, Row, Col, Button, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <Container>
      <Row className="my-5 text-center">
        <Col>
          <h1>Welcome to OptiCare24</h1>
          <p className="lead">
            A complete optical shop management system for retailers and eye care professionals
          </p>
          <div className="my-4">
            <Button as={Link} to="/login" variant="primary" size="lg" className="mx-2">
              Login
            </Button>
            <Button as={Link} to="/register" variant="outline-primary" size="lg" className="mx-2">
              Register
            </Button>
          </div>
        </Col>
      </Row>
      
      <Row className="my-5">
        <Col md={4} className="mb-4">
          <Card>
            <Card.Body>
              <Card.Title>Inventory Management</Card.Title>
              <Card.Text>
                Track frames, lenses, and accessories with low-stock alerts
                and detailed inventory reports.
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card>
            <Card.Body>
              <Card.Title>Prescription Tracking</Card.Title>
              <Card.Text>
                Securely store and manage customer prescriptions and connect
                them with the right products.
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card>
            <Card.Body>
              <Card.Title>QR Warranty System</Card.Title>
              <Card.Text>
                Generate and verify product warranties with our integrated
                QR-code based verification system.
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Row className="my-5">
        <Col md={6} className="mb-4">
          <h2>For Eye Care Professionals</h2>
          <p>
            OptiCare24 helps optometrists and opticians manage patient records,
            prescriptions, and appointments in one secure location.
          </p>
        </Col>
        <Col md={6} className="mb-4">
          <h2>For Optical Retailers</h2>
          <p>
            Streamline your inventory, sales, and customer management with
            our comprehensive optical shop solution.
          </p>
        </Col>
      </Row>
    </Container>
  );
};

export default Home;