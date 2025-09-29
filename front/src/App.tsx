import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AppNavbar from './components/Navbar';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import FlightRequestForm from './components/FlightRequestForm';
import ManageDestinations from './components/ManageDestinations';

// Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';
// React Toastify CSS
import 'react-toastify/dist/ReactToastify.css';
// React DatePicker CSS
import 'react-datepicker/dist/react-datepicker.css';

import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppNavbar />
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/request-flight"
              element={
                <ProtectedRoute requiredRole="client">
                  <FlightRequestForm />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/manage-destinations"
              element={
                <ProtectedRoute allowedRoles={['admin', 'operator']}>
                  <ManageDestinations />
                </ProtectedRoute>
              }
            />
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          
          <ToastContainer
            position="top-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
          />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
