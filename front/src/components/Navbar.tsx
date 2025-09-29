import React from 'react';
import { Navbar, Nav, NavDropdown, Container } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const AppNavbar: React.FC = () => {
  const { user, logout, isAuthenticated, isClient, isOperator, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
      <Container>
        <Navbar.Brand as={Link} to="/dashboard">
          ✈️ Evolution Fly App
        </Navbar.Brand>
        
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/dashboard">
              Dashboard
            </Nav.Link>
            
            {isClient && (
              <Nav.Link as={Link} to="/request-flight">
                Solicitar Vuelo
              </Nav.Link>
            )}
            
            {(isOperator || isAdmin) && (
              <>
                <Nav.Link as={Link} to="/manage-destinations">
                  Gestionar Destinos
                </Nav.Link>
                <Nav.Link as={Link} to="/flight-reports">
                  Reportes
                </Nav.Link>
              </>
            )}
          </Nav>
          
          <Nav>
            <NavDropdown
              title={`${user?.first_name} ${user?.last_name}`}
              id="user-nav-dropdown"
              align="end"
            >
              <NavDropdown.ItemText>
                <strong>Rol:</strong> {user?.role}
              </NavDropdown.ItemText>
              <NavDropdown.ItemText>
                <strong>Email:</strong> {user?.email}
              </NavDropdown.ItemText>
              <NavDropdown.Divider />
              <NavDropdown.Item as={Link} to="/profile">
                Mi Perfil
              </NavDropdown.Item>
              <NavDropdown.Divider />
              <NavDropdown.Item onClick={handleLogout}>
                Cerrar Sesión
              </NavDropdown.Item>
            </NavDropdown>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default AppNavbar;