import type { AxiosInstance } from "axios";
import globalAxios from "axios";
import type { User } from "firebase/auth";
import { getFirebaseAuth } from "../auth/firebase";
import { V1Api, type UserProfile } from "./axios-client/api";
import type { Configuration } from "./axios-client/configuration";

const BASE_PATH = import.meta.env.VITE_BACKEND_API_URL;

// Auth data interface
interface AuthData {
    token: string;
    user: UserProfile | null;
    currentProfile?: 'client' | 'service_provider' | null;
    clientProfile?: any | null;
    serviceProviderProfile?: any | null;
}

// LocalStorage key for auth data
const AUTH_STORAGE_KEY = "auth_data";

class MyApi extends V1Api {
    public axios: AxiosInstance = globalAxios;
    constructor(configuration?: Configuration, axiosInstance: AxiosInstance = globalAxios) {
        super(configuration, BASE_PATH, axiosInstance);
        this.axios.defaults.baseURL = BASE_PATH;
        this.setupInterceptors();
    }

    private setupInterceptors() {
        const guestRoutes = ["/api/v1/auth/firebase/", "/api/v1/auth/token/"];
        // Add request interceptor to include JWT token
        this.axios.interceptors.request.use(
            async (config) => {
                // Try to get JWT token from localStorage first
                const authData = this.getAuthFromStorage();

                if (guestRoutes.includes(config.url || "")) {
                    return config;
                }

                if (authData?.token) {
                    config.headers.Authorization = `Token ${authData.token}`;
                } else {
                    // Fallback to Firebase token if no JWT token
                    const firebaseUser = await this.getCurrentFirebaseUser();
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
        this.axios.interceptors.response.use(
            (response) => response,
            async (error) => {
                const originalRequest = error.config;

                if (error.response?.status === 401 && !originalRequest._retry) {
                    originalRequest._retry = true;

                    try {
                        // Try to refresh JWT token first
                        const result = await this.refreshBackendToken();
                        if (result.success && result.data.access_token) {
                            // Update localStorage with new token
                            const authData = this.getAuthFromStorage();
                            if (authData) {
                                authData.token = result.data.access_token;
                                this.setAuthToStorage(authData);
                            }
                            originalRequest.headers.Authorization = `Token ${result.data.access_token}`;
                            return this.axios(originalRequest);
                        }

                        // Fallback to Firebase token refresh
                        const firebaseUser = await this.getCurrentFirebaseUser();
                        if (firebaseUser) {
                            const token = await firebaseUser.getIdToken(true); // Force refresh
                            originalRequest.headers.Authorization = `Token ${token}`;
                            return this.axios(originalRequest);
                        }
                    } catch (refreshError) {
                        console.error("Token refresh failed:", refreshError);
                        // Clear auth data
                        this.clearAuthFromStorage();
                    }
                }

                return Promise.reject(error);
            },
        );
    }

    // Helper functions for localStorage
    private getAuthFromStorage = (): AuthData | null => {
        try {
            const stored = localStorage.getItem(AUTH_STORAGE_KEY);
            return stored ? JSON.parse(stored) : null;
        } catch (error) {
            console.error("Error reading auth data from localStorage:", error);
            return null;
        }
    };

    private setAuthToStorage = (authData: AuthData): void => {
        try {
            localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authData));
        } catch (error) {
            console.error("Error saving auth data to localStorage:", error);
        }
    };

    private clearAuthFromStorage = (): void => {
        try {
            localStorage.removeItem(AUTH_STORAGE_KEY);
        } catch (error) {
            console.error("Error clearing auth data from localStorage:", error);
        }
    };

    // Helper function to get current Firebase user
    private getCurrentFirebaseUser = async (): Promise<User | null> => {
        return new Promise((resolve) => {
            const auth = getFirebaseAuth();
            const unsubscribe = auth.onAuthStateChanged((user) => {
                unsubscribe();
                resolve(user);
            });
        });
    };

    // Authentication methods
    public async authenticateWithBackend(firebaseUser: User) {
        try {
            const token = await firebaseUser.getIdToken();
            const response = await this.axios.post("/api/v1/auth/firebase/", {
                id_token: token,
            });

            // Save essential auth data to localStorage
            const authData: AuthData = {
                token: response.data.token,
                user: {
                    id: response.data.user?.id || 0,
                    username: response.data.user?.username || "",
                    email: response.data.user?.email || firebaseUser.email || "",
                    groups: response.data.user?.groups || [],
                    permissions: response.data.user?.permissions || [],
                    is_active: response.data.user?.is_active || false,
                    is_staff: response.data.user?.is_staff || false,
                    is_superuser: response.data.user?.is_superuser || false,
                    date_joined: response.data.user?.date_joined,
                    last_login: response.data.user?.last_login,
                    photo_url: response.data.user?.photo_url || "",
                },
            };
            this.setAuthToStorage(authData);

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
    }

    public async refreshBackendToken() {
        try {
            const firebaseUser = await this.getCurrentFirebaseUser();
            if (!firebaseUser) {
                throw new Error("No authenticated user");
            }

            const token = await firebaseUser.getIdToken(true); // Force refresh
            const response = await this.axios.post("/auth/refresh/", {
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
    }

    // Public auth helper methods
    public getAuthData = (): AuthData | null => {
        return this.getAuthFromStorage();
    };

    public clearAuthData = (): void => {
        this.clearAuthFromStorage();
    };

    public isAuthenticated = (): boolean => {
        const authData = this.getAuthFromStorage();
        return !!(authData?.token && authData?.user);
    };

    // Profile management methods
    public setCurrentProfile = (profile: 'client' | 'service_provider' | null): void => {
        const authData = this.getAuthFromStorage();
        if (authData) {
            authData.currentProfile = profile;
            this.setAuthToStorage(authData);
        }
    };

    public setClientProfile = (profile: any | null): void => {
        const authData = this.getAuthFromStorage();
        if (authData) {
            authData.clientProfile = profile;
            this.setAuthToStorage(authData);
        }
    };

    public setServiceProviderProfile = (profile: any | null): void => {
        const authData = this.getAuthFromStorage();
        if (authData) {
            authData.serviceProviderProfile = profile;
            this.setAuthToStorage(authData);
        }
    };
}

const myApi = new MyApi();

export default myApi;