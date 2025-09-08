import axios from "axios";
import type { User } from "firebase/auth";

const BACKEND_API_URL =
  import.meta.env.VITE_BACKEND_API_URL || "http://localhost:8000/api/v1";

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: BACKEND_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include Firebase token
apiClient.interceptors.request.use(
  async (config) => {
    const firebaseUser = await getCurrentFirebaseUser();
    if (firebaseUser) {
      const token = await firebaseUser.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
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
        const firebaseUser = await getCurrentFirebaseUser();
        if (firebaseUser) {
          const token = await firebaseUser.getIdToken(true); // Force refresh
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        console.error("Token refresh failed:", refreshError);
        // Redirect to login or handle as needed
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
    const response = await apiClient.post("/auth/firebase/", {
      id_token: token,
      email: firebaseUser.email,
      uid: firebaseUser.uid,
    });

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

export { apiClient };
