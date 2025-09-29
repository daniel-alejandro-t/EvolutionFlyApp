import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Modal, Form, 
  Alert, Spinner, Badge 
} from 'react-bootstrap';
import { toast } from 'react-toastify';
import { destinationsAPI } from '../services/api';
import { Destination, CreateDestination } from '../types';

const ManageDestinations: React.FC = () => {
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingDestination, setEditingDestination] = useState<Destination | null>(null);
  const [formData, setFormData] = useState<CreateDestination>({
    name: '',
    code: '',
    description: '',
    is_active: true,
  });

  useEffect(() => {
    loadDestinations();
  }, []);

  const loadDestinations = async () => {
    try {
      const data = await destinationsAPI.getAll();
      setDestinations(data.results || data);
    } catch (error) {
      console.error('Error loading destinations:', error);
      toast.error('Error al cargar destinos');
    } finally {
      setLoading(false);
    }
  };

  const handleShowModal = (destination?: Destination) => {
    if (destination) {
      setEditingDestination(destination);
      setFormData({
        name: destination.name,
        code: destination.code,
        description: destination.description || '',
        is_active: destination.is_active,
      });
    } else {
      setEditingDestination(null);
      setFormData({
        name: '',
        code: '',
        description: '',
        is_active: true,
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingDestination(null);
    setFormData({
      name: '',
      code: '',
      description: '',
      is_active: true,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingDestination) {
        await destinationsAPI.update(editingDestination.id, formData);
        toast.success('Destino actualizado exitosamente');
      } else {
        await destinationsAPI.create(formData);
        toast.success('Destino creado exitosamente');
      }
      
      handleCloseModal();
      loadDestinations();
    } catch (error: any) {
      console.error('Error saving destination:', error);
      toast.error('Error al guardar destino');
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (window.confirm(`¿Estás seguro de eliminar el destino "${name}"?`)) {
      try {
        await destinationsAPI.delete(id);
        toast.success('Destino eliminado exitosamente');
        loadDestinations();
      } catch (error) {
        console.error('Error deleting destination:', error);
        toast.error('Error al eliminar destino');
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<any>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
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
          <div className="d-flex justify-content-between align-items-center">
            <h2>🌍 Gestión de Destinos</h2>
            <Button variant="primary" onClick={() => handleShowModal()}>
              ➕ Nuevo Destino
            </Button>
          </div>
        </Col>
      </Row>

      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Lista de Destinos</h5>
            </Card.Header>
            <Card.Body>
              {destinations.length === 0 ? (
                <Alert variant="info">
                  No hay destinos registrados. Crea el primer destino.
                </Alert>
              ) : (
                <Table responsive striped hover>
                  <thead>
                    <tr>
                      <th>Nombre</th>
                      <th>Código</th>
                      <th>Descripción</th>
                      <th>Estado</th>
                      <th>Creado</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {destinations.map((destination) => (
                      <tr key={destination.id}>
                        <td><strong>{destination.name}</strong></td>
                        <td>
                          <Badge bg="secondary">{destination.code}</Badge>
                        </td>
                        <td>
                          {destination.description || (
                            <em className="text-muted">Sin descripción</em>
                          )}
                        </td>
                        <td>
                          <Badge bg={destination.is_active ? 'success' : 'danger'}>
                            {destination.is_active ? 'Activo' : 'Inactivo'}
                          </Badge>
                        </td>
                        <td>
                          {new Date(destination.created_at).toLocaleDateString('es-EC')}
                        </td>
                        <td>
                          <div className="d-flex gap-2">
                            <Button
                              size="sm"
                              variant="outline-primary"
                              onClick={() => handleShowModal(destination)}
                            >
                              ✏️ Editar
                            </Button>
                            <Button
                              size="sm"
                              variant="outline-danger"
                              onClick={() => handleDelete(destination.id, destination.name)}
                            >
                              🗑️ Eliminar
                            </Button>
                          </div>
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

      {/* Modal for Create/Edit */}
      <Modal show={showModal} onHide={handleCloseModal}>
        <Modal.Header closeButton>
          <Modal.Title>
            {editingDestination ? 'Editar Destino' : 'Nuevo Destino'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Nombre de la Ciudad</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Ej: Quito"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Código IATA</Form.Label>
              <Form.Control
                type="text"
                name="code"
                value={formData.code}
                onChange={handleChange}
                required
                placeholder="Ej: UIO"
                maxLength={3}
                style={{ textTransform: 'uppercase' }}
              />
              <Form.Text className="text-muted">
                Código de 3 letras para el aeropuerto
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Descripción (opcional)</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Descripción de la ciudad o información adicional"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
                label="Destino activo (disponible para solicitudes)"
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {editingDestination ? 'Actualizar' : 'Crear'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
};

export default ManageDestinations;