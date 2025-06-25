import React from 'react';
import { Navigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactElement;
}

const AuthRoute = ({ children }: ProtectedRouteProps) => {
  const token = localStorage.getItem('authToken');
  return token ? <Navigate to="/" replace /> : children;
};

export default AuthRoute;
