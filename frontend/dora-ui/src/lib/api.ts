import axios from 'axios';

export interface Release {
  id: string;
  platform: string;
  release_type: string;
  is_successful: boolean;
  version: string;
  rollout_date: string;
  mcm_link?: string;
  ci_job_link?: string;
  commit_list_link?: string;
}

export interface CreateReleaseData {
  platform: string;
  release_type: string;
  is_successful: boolean;
  version: string;
  rollout_date: string;
  mcm_link?: string;
  ci_job_link?: string;
  commit_list_link?: string;
}

export interface LoginResponse {
  user: {
    id: string;
    username: string;
    role: string;
  };
}

export interface AuthStatus {
  authenticated: boolean;
}

export interface MetricsData {
  deployment_frequency: {
    value: number;
    trend: number;
    history: Array<{ date: string; value: number }>;
  };
  lead_time: {
    value: number;
    trend: number;
    history: Array<{ date: string; value: number }>;
  };
  time_to_restore: {
    value: number;
    trend: number;
    history: Array<{ date: string; value: number }>;
  };
  change_failure_rate: {
    value: number;
    trend: number;
    history: Array<{ date: string; value: number }>;
  };
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});



// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Return error message from the server if available
      if (error.response.data) {
        const errorMessage = error.response.data.error || error.response.data.message;
        if (errorMessage) {
          return Promise.reject(new Error(errorMessage));
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const auth = {
  register: async (username: string, password: string, role = 'user', email?: string): Promise<void> => {
    await api.post('auth/register', { username, password, role, email });
  },
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('auth/login', { username, password });
    return response.data;
  },
  logout: async (navigate: (path: string) => void) => {
    await api.post('auth/logout');
    navigate('/login');
  },
  status: async (): Promise<AuthStatus> => {
    const response = await api.get<AuthStatus>('auth/status');
    return response.data;
  },
};

// Releases endpoints
export const releases = {
  getAll: async (): Promise<Release[]> => {
    const response = await api.get<Release[]>('releases/');
    return response.data;
  },
  create: async (data: CreateReleaseData): Promise<Release> => {
    const response = await api.post<Release>('releases/', data);
    return response.data;
  },
  update: async (id: string, data: CreateReleaseData): Promise<Release> => {
    const response = await api.put<Release>(`releases/${id}`, data);
    return response.data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`releases/${id}`);
  },
};

// Metrics endpoints
export const metrics = {
  get: async (start_date: string, end_date: string): Promise<MetricsData> => {
  const response = await api.get<MetricsData>(`metrics/`, {
    params: { start_date, end_date}
  });
  return response.data;
  },
  getDeploymentVolume: async (start_date: string, end_date: string) => {
  const response = await api.get<Array<{
    date: string;
    Android?: number;
    Samsung?: number;
    Roku?: number;
    Xbox?: number;
    PS4?: number;
    PS5?: number;
  }>>('metrics/deployment-volume', {
    params: { start_date, end_date }
  });
  return response.data;
},

};

export default api;
