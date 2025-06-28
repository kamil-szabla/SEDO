import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { auth } from '../lib/api';

interface AuthRouteProps {
  children: React.ReactElement;
}

const AuthRoute = ({ children }: AuthRouteProps) => {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    auth.status()
      .then((res) => {
        setAuthenticated(res.authenticated);
      })
      .catch(() => {
        setAuthenticated(false);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return authenticated ? <Navigate to="/" replace /> : children;
};

export default AuthRoute;
