import { CUrls } from "@/config/constants";
import { useAuthStore } from "@/stores/auth-store";
import type { AxiosInstance } from "axios";
import globalAxios from "axios";
import type { User as FirebaseUser } from "firebase/auth";
import { getFirebaseAuth } from "../auth/firebase";
import { V1Api } from "./axios-client/api";
import type { Configuration } from "./axios-client/configuration";

const BASE_PATH = CUrls.BACKEND_API_URL;


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
                const auth = useAuthStore.getState();

                if (guestRoutes.includes(config.url || "")) {
                    return config;
                }

                if (auth?.token) {
                    config.headers.Authorization = `Token ${auth.token}`;
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
                const auth = useAuthStore.getState();

                if (error.response?.status === 401 && !originalRequest._retry) {
                    originalRequest._retry = true;

                    try {
                        // Try to refresh JWT token first
                        const result = await this.refreshBackendToken();
                        if (result.success && result.data.access_token) {
                            auth.setToken(result.data.access_token);
                            originalRequest.headers.Authorization = `Token ${result.data.access_token}`;
                            return this.axios(originalRequest);
                        }

                        const firebaseUser = await this.getCurrentFirebaseUser();
                        if (firebaseUser) {
                            const token = await firebaseUser.getIdToken(true); // Force refresh
                            originalRequest.headers.Authorization = `Token ${token}`;
                            return this.axios(originalRequest);
                        }
                    } catch (refreshError) {
                        console.error("Token refresh failed:", refreshError);
                        // Clear auth data
                        auth.setToken(null);
                    }
                }

                return Promise.reject(error);
            },
        );
    }

    // Helper function to get current Firebase user
    private getCurrentFirebaseUser = async (): Promise<FirebaseUser | null> => {
        return new Promise((resolve) => {
            const auth = getFirebaseAuth();
            const unsubscribe = auth.onAuthStateChanged((user) => {
                unsubscribe();
                resolve(user);
            });
        });
    };

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
}

const myApi = new MyApi();

export default myApi;