import { authenticateWithBackend, getAuthData, clearAuthData, isAuthenticated as checkAuth } from "@/lib/auth/backend-service";
import { type User } from "firebase/auth";
import { create } from "zustand";

interface AuthUser {
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
}

interface AuthState {
  auth: {
    user: AuthUser | null;
    firebaseUser: User | null;
    isLoading: boolean;
    setUser: (user: AuthUser | null) => void;
    setFirebaseUser: (user: User | null) => void;
    setLoading: (loading: boolean) => void;
    reset: () => void;
    authenticateWithBackend: (firebaseUser: User) => Promise<void>;
    loadFromStorage: () => void;
    isAuthenticated: () => boolean;
  };
}

export const useAuthStore = create<AuthState>()((set) => {
  return {
    auth: {
      user: null,
      firebaseUser: null,
      isLoading: false,
      setUser: (user) =>
        set((state) => ({ ...state, auth: { ...state.auth, user } })),
      setFirebaseUser: (firebaseUser) =>
        set((state) => ({ ...state, auth: { ...state.auth, firebaseUser } })),
      setLoading: (isLoading) =>
        set((state) => ({ ...state, auth: { ...state.auth, isLoading } })),
      reset: () =>
        set((state) => {
          clearAuthData();
          return {
            ...state,
            auth: {
              ...state.auth,
              user: null,
              firebaseUser: null,
              isLoading: false,
            },
          };
        }),
      loadFromStorage: () => {
        const authData = getAuthData();
        if (authData?.user) {
          set((state) => {
            // Only update if user is not already loaded
            if (!state.auth.user) {
              return {
                ...state,
                auth: {
                  ...state.auth,
                  user: authData.user,
                },
              };
            }
            return state;
          });
        }
      },
      isAuthenticated: () => {
        return checkAuth();
      },
      authenticateWithBackend: async (firebaseUser: User) => {
        set((state) => ({
          ...state,
          auth: { ...state.auth, isLoading: true },
        }));

        try {
          const result = await authenticateWithBackend(firebaseUser);

          if (result.success) {
            // Load complete user data from localStorage (set by backend service)
            const authData = getAuthData();
            const backendUser: AuthUser = authData?.user || {
              id: 0,
              username: firebaseUser.displayName || "",
              email: firebaseUser.email || "",
              name: firebaseUser.displayName || "",
              user_role: "client",
              groups: [],
              permissions: [],
              is_active: false,
              is_staff: false,
              is_superuser: false,
            };

            set((state) => ({
              ...state,
              auth: {
                ...state.auth,
                user: backendUser,
                firebaseUser,
                isLoading: false,
              },
            }));
          } else {
            throw new Error(result.error);
          }
        } catch (error) {
          console.error("Backend authentication failed:", error);
          set((state) => ({
            ...state,
            auth: { ...state.auth, isLoading: false },
          }));
          throw error;
        }
      },
    },
  };
});
