import { Navigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: JSX.Element;
}

const AuthRoute = ({ children }: ProtectedRouteProps) => {
  const token = localStorage.getItem('authToken');
  return token ? <Navigate to="/" replace /> : children;
};

export default AuthRoute;
