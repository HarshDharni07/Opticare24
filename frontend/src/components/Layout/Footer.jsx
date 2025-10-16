/**
 * Footer Component
 * Purpose: Site-wide footer with company info and links
 * Reference: PROMPT.md → Frontend structure
 */

import { Container, Row, Col } from 'react-bootstrap';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-light py-4 mt-auto">
      <Container>
        <Row>
          <Col md={6} className="text-center text-md-start">
            <h5>OptiCare24</h5>
            <p className="text-muted small mb-0">
              Optical Shop Management System &copy; {currentYear}
            </p>
          </Col>
          <Col md={6} className="text-center text-md-end">
            <ul className="list-inline mb-0">
              <li className="list-inline-item">
                <a href="#" className="text-decoration-none text-muted">Privacy Policy</a>
              </li>
              <li className="list-inline-item">•</li>
              <li className="list-inline-item">
                <a href="#" className="text-decoration-none text-muted">Terms of Use</a>
              </li>
              <li className="list-inline-item">•</li>
              <li className="list-inline-item">
                <a href="#" className="text-decoration-none text-muted">Support</a>
              </li>
            </ul>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;