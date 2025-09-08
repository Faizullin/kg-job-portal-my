import { authenticateWithBackend } from "@/lib/auth/backend-service";
import { getCookie, removeCookie, setCookie } from "@/lib/cookies";
import { type User } from "firebase/auth";
import { create } from "zustand";

const ACCESS_TOKEN = "thisisjustarandomstring";

interface AuthUser {
  accountNo: string;
  email: string;
  role: string[];
  exp: number;
  uid: string;
}

interface AuthState {
  auth: {
    user: AuthUser | null;
    firebaseUser: User | null;
    isLoading: boolean;
    setUser: (user: AuthUser | null) => void;
    setFirebaseUser: (user: User | null) => void;
    setLoading: (loading: boolean) => void;
    accessToken: string;
    setAccessToken: (accessToken: string) => void;
    resetAccessToken: () => void;
    reset: () => void;
    authenticateWithBackend: (firebaseUser: User) => Promise<void>;
  };
}

export const useAuthStore = create<AuthState>()((set) => {
  const cookieState = getCookie(ACCESS_TOKEN);
  const initToken = cookieState ? JSON.parse(cookieState) : "";

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
      accessToken: initToken,
      setAccessToken: (accessToken) =>
        set((state) => {
          setCookie(ACCESS_TOKEN, JSON.stringify(accessToken));
          return { ...state, auth: { ...state.auth, accessToken } };
        }),
      resetAccessToken: () =>
        set((state) => {
          removeCookie(ACCESS_TOKEN);
          return { ...state, auth: { ...state.auth, accessToken: "" } };
        }),
      reset: () =>
        set((state) => {
          removeCookie(ACCESS_TOKEN);
          return {
            ...state,
            auth: {
              ...state.auth,
              user: null,
              firebaseUser: null,
              accessToken: "",
              isLoading: false,
            },
          };
        }),
      authenticateWithBackend: async (firebaseUser: User) => {
        set((state) => ({
          ...state,
          auth: { ...state.auth, isLoading: true },
        }));

        try {
          const result = await authenticateWithBackend(firebaseUser);

          if (result.success) {
            const backendUser: AuthUser = {
              accountNo: result.data.account_no || "ACC001",
              email: firebaseUser.email || "",
              role: result.data.roles || ["user"],
              exp: result.data.exp || Date.now() + 24 * 60 * 60 * 1000,
              uid: firebaseUser.uid,
            };

            set((state) => ({
              ...state,
              auth: {
                ...state.auth,
                user: backendUser,
                firebaseUser,
                accessToken: result.data.access_token || "",
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
