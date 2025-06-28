import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from '../lib/api';

interface ProtectedRouteProps {
  children: React.ReactElement;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    auth.status()
      .then((res) => {
        setAuthenticated(res.authenticated);
        if (!res.authenticated) {
          navigate('/login');
        }
      })
      .catch(() => {
        navigate('/login');
      })
      .finally(() => setLoading(false));
  }, [navigate]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return authenticated ? children : null;
};

export default ProtectedRoute;
