import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import DatePicker from 'react-datepicker';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { destinationsAPI, flightRequestsAPI } from '../services/api';
import { Destination, CreateFlightRequest } from '../types';
import { useAuth } from '../contexts/AuthContext';
import "react-datepicker/dist/react-datepicker.css";

const FlightRequestForm: React.FC = () => {
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingDestinations, setLoadingDestinations] = useState(true);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState<CreateFlightRequest>({
    destination: 0,
    travel_date: '',
    notes: '',
  });
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadDestinations();
  }, []);

  const loadDestinations = async () => {
    try {
      // Use cached destinations endpoint
      const data = await destinationsAPI.getActive();
      setDestinations(data);
    } catch (error) {
      console.error('Error loading destinations:', error);
      toast.error('Error al cargar destinos');
    } finally {
      setLoadingDestinations(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.destination) {
      setError('Por favor selecciona un destino');
      return;
    }

    if (!selectedDate) {
      setError('Por favor selecciona una fecha de viaje');
      return;
    }

    // Check if date is in the future
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (selectedDate <= today) {
      setError('La fecha de viaje debe ser futura');
      return;
    }

    setLoading(true);

    try {
      const requestData: CreateFlightRequest = {
        ...formData,
        travel_date: selectedDate.toISOString().split('T')[0], // Format as YYYY-MM-DD
      };

      await flightRequestsAPI.create(requestData);
      toast.success('¡Solicitud de vuelo creada exitosamente!');
      navigate('/dashboard');
    } catch (error: any) {
      console.error('Error creating flight request:', error);
      setError(error.response?.data?.message || 'Error al crear solicitud de vuelo');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<any>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'destination' ? parseInt(value) : value,
    }));
  };

  const handleDateChange = (date: Date | null) => {
    setSelectedDate(date);
  };

  if (loadingDestinations) {
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
      <Row>
        <Col md={8} lg={6} className="mx-auto">
          <Card className="shadow">
            <Card.Header className="bg-info text-white">
              <h3 className="mb-0">✈️ Solicitar Vuelo</h3>
              <small>Usuario: {user?.first_name} {user?.last_name}</small>
            </Card.Header>
            <Card.Body>
              {error && <Alert variant="danger">{error}</Alert>}
              
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-4">
                  <Form.Label>
                    <strong>Destino</strong>
                  </Form.Label>
                  <Form.Select
                    name="destination"
                    value={formData.destination}
                    onChange={handleChange}
                    required
                    size="lg"
                  >
                    <option value="">Selecciona tu destino...</option>
                    {destinations.map((destination) => (
                      <option key={destination.id} value={destination.id}>
                        {destination.name} ({destination.code})
                        {destination.description && ` - ${destination.description}`}
                      </option>
                    ))}
                  </Form.Select>
                  {destinations.length === 0 && (
                    <Form.Text className="text-warning">
                      No hay destinos disponibles en este momento
                    </Form.Text>
                  )}
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label>
                    <strong>Fecha de Viaje</strong>
                  </Form.Label>
                  <div>
                    <DatePicker
                      selected={selectedDate}
                      onChange={handleDateChange}
                      minDate={new Date()}
                      dateFormat="dd/MM/yyyy"
                      placeholderText="Selecciona la fecha de viaje"
                      className="form-control form-control-lg"
                      required
                    />
                  </div>
                  <Form.Text className="text-muted">
                    La fecha debe ser futura
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label>
                    <strong>Notas adicionales (opcional)</strong>
                  </Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={4}
                    name="notes"
                    value={formData.notes}
                    onChange={handleChange}
                    placeholder="Agrega cualquier información adicional sobre tu viaje..."
                  />
                </Form.Group>

                <div className="d-grid gap-2">
                  <Button
                    variant="info"
                    type="submit"
                    size="lg"
                    disabled={loading || destinations.length === 0}
                  >
                    {loading ? (
                      <>
                        <Spinner
                          as="span"
                          animation="border"
                          size="sm"
                          role="status"
                          aria-hidden="true"
                          className="me-2"
                        />
                        Procesando solicitud...
                      </>
                    ) : (
                      '🚀 Solicitar Vuelo'
                    )}
                  </Button>
                  
                  <Button
                    variant="outline-secondary"
                    onClick={() => navigate('/dashboard')}
                    disabled={loading}
                  >
                    Cancelar
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default FlightRequestForm;