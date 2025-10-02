import type { UserDetail } from "@/lib/api/axios-client";
import myApi from "@/lib/api/my-api";
import { type User as FirebaseUser } from "firebase/auth";
import { create } from "zustand";
import { persist } from "zustand/middleware";

export type ProfileType = 'client' | 'master';

interface AuthState {
  token: string | null;
  setToken: (token: string | null) => void;
  isAuthenticated: boolean;
  setIsAuthenticated: (isAuthenticated: boolean) => void;
  user: UserDetail | null;
  setUser: (user: UserDetail | null) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  currentProfileType: ProfileType | null;
  setCurrentProfileType: (profile: ProfileType | null) => void;
  reset: () => void;
  authenticateWithBackend: (firebaseUser: FirebaseUser) => Promise<void>;
  getProfile: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist((set) => ({
    token: null,
    setToken: (token) =>
      set((state) => ({ ...state, token })),
    isAuthenticated: false,
    setIsAuthenticated: (isAuthenticated) =>
      set((state) => ({ ...state, isAuthenticated })),
    user: null,
    setUser: (user) =>
      set((state) => ({ ...state, user })),
    isLoading: false,
    setIsLoading: (isLoading) =>
      set((state) => ({ ...state, isLoading })),
    currentProfileType: null,
    setCurrentProfileType: (currentProfileType) => {
      set((state) => ({ ...state, currentProfileType }))
    },
    reset: () =>
      set(() => {
        return {
          token: null,
          user: null,
          currentProfileType: null,
          firebaseUser: null,
          isLoading: false,
        };
      }),
    authenticateWithBackend: async (firebaseUser: FirebaseUser) => {
      set((state) => ({
        ...state,
        isLoading: true,
      }));

      try {
        const token = await firebaseUser.getIdToken();
        const response = await myApi.axios.post<{
          user: UserDetail;
          token: string;
          message: string;
        }>("/api/v1/auth/firebase/", {
          id_token: token,
        });
        const authData = response.data;
        if (authData.user) {
          set((state) => ({
            ...state,
            user: authData.user,
            token: authData.token,
            isLoading: false,
            isAuthenticated: true,
          }));
        } else {
          set((state) => ({
            ...state,
            user: null,
            token: null,
            isLoading: false,
            isAuthenticated: false,
          }));
        }
      } catch (error) {
        console.error("Backend authentication failed:", error);
        set((state) => ({
          ...state,
          isLoading: false,
        }));
        throw error;
      }
    },
    getProfile: async () => {
      try {
        const profile = await myApi.v1ProfileRetrieve();
        set((state) => ({
          ...state,
          profile: profile,
        }));
      } catch (error) {
        console.error("Failed to fetch profile:", error);
        throw error;
      }
    },
  }), {
    name: "auth-store",
  }),
);