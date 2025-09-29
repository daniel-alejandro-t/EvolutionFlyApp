import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Spinner, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { flightRequestsAPI } from '../services/api';
import { FlightRequest } from '../types';
import { useAuth } from '../contexts/AuthContext';

const Dashboard: React.FC = () => {
  const [flightRequests, setFlightRequests] = useState<FlightRequest[]>([]);
  const [pendingRequests, setPendingRequests] = useState<FlightRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const { user, isClient, isOperator, isAdmin } = useAuth();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load user's flight requests (all users)
      const userRequests = await flightRequestsAPI.getAll();
      setFlightRequests(userRequests.results || userRequests);

      // Load pending requests (only for operators and admins)
      if (isOperator || isAdmin) {
        try {
          const pending = await flightRequestsAPI.getPending();
          setPendingRequests(pending.results || pending);
        } catch (err) {
          console.error('Error loading pending requests:', err);
        }
      }
    } catch (error: any) {
      console.error('Error loading data:', error);
      setError('Error al cargar los datos');
    } finally {
      setLoading(false);
    }
  };

  const handleReserve = async (requestId: number, operatorNotes?: string) => {
    try {
      await flightRequestsAPI.reserve(requestId, operatorNotes);
      toast.success('Solicitud reservada exitosamente');
      loadData(); // Reload data
    } catch (error: any) {
      console.error('Error reserving flight:', error);
      toast.error('Error al reservar vuelo');
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: { [key: string]: string } = {
      pending: 'warning',
      reserved: 'success',
      cancelled: 'danger',
      completed: 'secondary',
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-EC', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <Container className="d-flex justify-content-center align-items-center min-vh-100">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Cargando...</span>
        </Spinner>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <Row className="mb-4">
        <Col>
          <h2>Dashboard - Bienvenido {user?.first_name}!</h2>
          <p className="text-muted">
            Rol: <Badge bg="info">{user?.role}</Badge>
          </p>
        </Col>
      </Row>

      {error && <Alert variant="danger">{error}</Alert>}

      {/* Action Buttons */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Body>
              <h5>Acciones Rápidas</h5>
              <div className="d-flex gap-2 flex-wrap">
                {isClient && (
                  <Link to="/request-flight">
                    <Button
                      variant="primary"
                      size="lg"
                    >
                      ✈️ Solicitar Vuelo
                    </Button>
                  </Link>
                )}
                
                {(isOperator || isAdmin) && (
                  <>
                    <Link to="/manage-destinations">
                      <Button variant="success">
                        🌍 Gestionar Destinos
                      </Button>
                    </Link>
                    <Link to="/flight-reports">
                      <Button variant="info">
                        📊 Reportes
                      </Button>
                    </Link>
                  </>
                )}
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Pending Requests (Operators/Admins Only) */}
      {(isOperator || isAdmin) && (
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Header>
                <h5 className="mb-0">
                  📋 Solicitudes Pendientes 
                  <Badge bg="warning" className="ms-2">
                    {pendingRequests.length}
                  </Badge>
                </h5>
              </Card.Header>
              <Card.Body>
                {pendingRequests.length === 0 ? (
                  <Alert variant="info">No hay solicitudes pendientes</Alert>
                ) : (
                  <Table responsive striped hover>
                    <thead>
                      <tr>
                        <th>Cliente</th>
                        <th>Destino</th>
                        <th>Fecha de Viaje</th>
                        <th>Días Restantes</th>
                        <th>Notas</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pendingRequests.map((request) => (
                        <tr key={request.id}>
                          <td>
                            <strong>
                              {request.user.first_name} {request.user.last_name}
                            </strong>
                            <br />
                            <small className="text-muted">{request.user.email}</small>
                          </td>
                          <td>
                            <strong>{request.destination.name}</strong>
                            <br />
                            <small className="text-muted">({request.destination.code})</small>
                          </td>
                          <td>{formatDate(request.travel_date)}</td>
                          <td>
                            {request.days_until_travel !== null && request.days_until_travel !== undefined ? (
                              <Badge 
                                bg={request.days_until_travel <= 7 ? 'warning' : 'secondary'}
                              >
                                {request.days_until_travel} días
                              </Badge>
                            ) : (
                              '-'
                            )}
                          </td>
                          <td>
                            {request.notes ? (
                              <small>{request.notes}</small>
                            ) : (
                              <em className="text-muted">Sin notas</em>
                            )}
                          </td>
                          <td>
                            <Button
                              size="sm"
                              variant="success"
                              onClick={() => handleReserve(request.id)}
                            >
                              ✅ Reservar
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* User's Flight Requests */}
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">
                {isClient ? '✈️ Mis Solicitudes de Vuelo' : '📈 Todas las Solicitudes'}
              </h5>
            </Card.Header>
            <Card.Body>
              {flightRequests.length === 0 ? (
                <Alert variant="info">
                  {isClient 
                    ? 'No tienes solicitudes de vuelo. ¡Crea tu primera solicitud!'
                    : 'No hay solicitudes de vuelo en el sistema'
                  }
                </Alert>
              ) : (
                <Table responsive striped hover>
                  <thead>
                    <tr>
                      {!isClient && <th>Cliente</th>}
                      <th>Destino</th>
                      <th>Fecha de Viaje</th>
                      <th>Estado</th>
                      <th>Creado</th>
                      {(isOperator || isAdmin) && <th>Reservado por</th>}
                    </tr>
                  </thead>
                  <tbody>
                    {flightRequests.map((request) => (
                      <tr key={request.id}>
                        {!isClient && (
                          <td>
                            <strong>
                              {request.user.first_name} {request.user.last_name}
                            </strong>
                            <br />
                            <small className="text-muted">{request.user.email}</small>
                          </td>
                        )}
                        <td>
                          <strong>{request.destination.name}</strong>
                          <br />
                          <small className="text-muted">({request.destination.code})</small>
                        </td>
                        <td>{formatDate(request.travel_date)}</td>
                        <td>{getStatusBadge(request.status)}</td>
                        <td>{formatDate(request.created_at)}</td>
                        {(isOperator || isAdmin) && (
                          <td>
                            {request.reserved_by ? (
                              <>
                                <strong>
                                  {request.reserved_by.first_name} {request.reserved_by.last_name}
                                </strong>
                                <br />
                                <small className="text-muted">
                                  {request.reserved_at && formatDate(request.reserved_at)}
                                </small>
                              </>
                            ) : (
                              <em className="text-muted">-</em>
                            )}
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;