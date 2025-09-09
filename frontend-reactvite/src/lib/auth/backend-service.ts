import axios from "axios";
import type { User } from "firebase/auth";

const BACKEND_API_URL = import.meta.env.VITE_BACKEND_API_URL;

// LocalStorage key for auth data
const AUTH_STORAGE_KEY = "auth_data";

// Auth data interface
interface AuthData {
  token: string;
  user: {
    id: number;
    username: string;
    email: string;
    name: string;
    user_role: string;
    groups: string[];
    permissions: string[];
    is_active: boolean;
    is_staff: boolean;
    is_superuser: boolean;
  } | null;
}

// Helper functions for localStorage
const getAuthFromStorage = (): AuthData | null => {
  try {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.error("Error reading auth data from localStorage:", error);
    return null;
  }
};

const setAuthToStorage = (authData: AuthData): void => {
  try {
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authData));
  } catch (error) {
    console.error("Error saving auth data to localStorage:", error);
  }
};

const clearAuthFromStorage = (): void => {
  try {
    localStorage.removeItem(AUTH_STORAGE_KEY);
  } catch (error) {
    console.error("Error clearing auth data from localStorage:", error);
  }
};

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: BACKEND_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include JWT token
apiClient.interceptors.request.use(
  async (config) => {
    // Try to get JWT token from localStorage first
    const authData = getAuthFromStorage();

    if (authData?.token) {
      config.headers.Authorization = `Token ${authData.token}`;
    } else {
      // Fallback to Firebase token if no JWT token
      const firebaseUser = await getCurrentFirebaseUser();
      if (firebaseUser) {
        const token = await firebaseUser.getIdToken();
        config.headers.Authorization = `Token ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Add response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh JWT token first
        const result = await refreshBackendToken();
        if (result.success && result.data.access_token) {
          // Update localStorage with new token
          const authData = getAuthFromStorage();
          if (authData) {
            authData.token = result.data.access_token;
            setAuthToStorage(authData);
          }
          originalRequest.headers.Authorization = `Token  ${result.data.access_token}`;
          return apiClient(originalRequest);
        }

        // Fallback to Firebase token refresh
        const firebaseUser = await getCurrentFirebaseUser();
        if (firebaseUser) {
          const token = await firebaseUser.getIdToken(true); // Force refresh
          originalRequest.headers.Authorization = `Token ${token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        console.error("Token refresh failed:", refreshError);
        // Clear auth data and redirect to login
        clearAuthFromStorage();
      }
    }

    return Promise.reject(error);
  },
);

// Helper function to get current Firebase user
const getCurrentFirebaseUser = async (): Promise<User | null> => {
  const { getFirebaseAuth } = await import("./firebase");
  return new Promise((resolve) => {
    const auth = getFirebaseAuth();
    const unsubscribe = auth.onAuthStateChanged((user) => {
      unsubscribe();
      resolve(user);
    });
  });
};

// Backend authentication functions
export const authenticateWithBackend = async (firebaseUser: User) => {
  try {
    const token = await firebaseUser.getIdToken();
    const apuClientWihtoutAuth = apiClient.create({
      headers: {
        "Content-Type": "application/json",
        Authorization: undefined,
      },
    });
    const response = await apuClientWihtoutAuth.post("/auth/firebase/", {
      id_token: token,
    });

    // Save essential auth data to localStorage
    const authData: AuthData = {
      token: response.data.token,
      user: {
        id: response.data.user?.id || 0,
        username: response.data.user?.username || firebaseUser.displayName || "",
        email: response.data.user?.email || firebaseUser.email || "",
        name: response.data.user?.name || firebaseUser.displayName || "",
        user_role: response.data.user?.user_role || "client",
        groups: response.data.user?.groups || [],
        permissions: response.data.user?.permissions || [],
        is_active: response.data.user?.is_active || false,
        is_staff: response.data.user?.is_staff || false,
        is_superuser: response.data.user?.is_superuser || false,
      },
    };
    setAuthToStorage(authData);

    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error("Backend authentication failed:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Authentication failed",
    };
  }
};

export const refreshBackendToken = async () => {
  try {
    const firebaseUser = await getCurrentFirebaseUser();
    if (!firebaseUser) {
      throw new Error("No authenticated user");
    }

    const token = await firebaseUser.getIdToken(true); // Force refresh
    const response = await apiClient.post("/auth/refresh/", {
      id_token: token,
    });

    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error("Token refresh failed:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Token refresh failed",
    };
  }
};

// Export localStorage helper functions
export const getAuthData = (): AuthData | null => {
  return getAuthFromStorage();
};

export const clearAuthData = (): void => {
  clearAuthFromStorage();
};

export const isAuthenticated = (): boolean => {
  const authData = getAuthFromStorage();
  return !!(authData?.token && authData?.user);
};

export { apiClient };
