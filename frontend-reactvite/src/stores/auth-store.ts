import type { ServiceProvider, UserProfile } from "@/lib/api/axios-client";
import { type User } from "firebase/auth";
import { create } from "zustand";
import { persist } from "zustand/middleware";

type AuthUser = UserProfile;

export type ProfileType = 'client' | 'service_provider';

interface AuthState {
  user: AuthUser | null;
  firebaseUser: User | null;
  isLoading: boolean;
  currentProfile: ProfileType | null;
  clientProfile: Client | null;
  serviceProviderProfile: ServiceProvider | null;
  setUser: (user: AuthUser | null) => void;
  setFirebaseUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setCurrentProfile: (profile: ProfileType | null) => void;
  setClientProfile: (profile: Client | null) => void;
  setServiceProviderProfile: (profile: ServiceProvider | null) => void;
  reset: () => void;
  authenticateWithBackend: (firebaseUser: User) => Promise<void>;
  loadFromStorage: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  //   (set) => {
  //   return {
  //     auth: {
  //       user: null,
  //       userProfile: null,
  //       firebaseUser: null,
  //       isLoading: false,
  //       isProfileLoading: false,
  //       currentProfile: null,
  //       clientProfile: null,
  //       serviceProviderProfile: null,
  //       setUser: (user) =>
  //         set((state) => ({ ...state, auth: { ...state.auth, user } })),
  //       setFirebaseUser: (firebaseUser) =>
  //         set((state) => ({ ...state, auth: { ...state.auth, firebaseUser } })),
  //       setLoading: (isLoading) =>
  //         set((state) => ({ ...state, auth: { ...state.auth, isLoading } })),
  //       setCurrentProfile: (currentProfile) => {
  //         myApi.setCurrentProfile(currentProfile);
  //         set((state) => ({ ...state, auth: { ...state.auth, currentProfile } }));
  //       },
  //       setClientProfile: (clientProfile) => {
  //         myApi.setClientProfile(clientProfile);
  //         set((state) => ({ ...state, auth: { ...state.auth, clientProfile } }));
  //       },
  //       setServiceProviderProfile: (serviceProviderProfile) => {
  //         myApi.setServiceProviderProfile(serviceProviderProfile);
  //         set((state) => ({ ...state, auth: { ...state.auth, serviceProviderProfile } }));
  //       },
  //       reset: () =>
  //         set((state) => {
  //           myApi.clearAuthData();
  //           return {
  //             ...state,
  //             auth: {
  //               ...state.auth,
  //               user: null,
  //               userProfile: null,
  //               firebaseUser: null,
  //               isLoading: false,
  //               isProfileLoading: false,
  //               currentProfile: null,
  //               clientProfile: null,
  //               serviceProviderProfile: null,
  //             },
  //           };
  //         }),
  //       loadFromStorage: () => {
  //         const authData = myApi.getAuthData();
  //         if (authData?.user) {
  //           set((state) => {
  //             // Only update if user is not already loaded
  //             if (!state.auth.user) {
  //               return {
  //                 ...state,
  //                 auth: {
  //                   ...state.auth,
  //                   user: authData.user,
  //                   currentProfile: authData.currentProfile || null,
  //                   clientProfile: authData.clientProfile || null,
  //                   serviceProviderProfile: authData.serviceProviderProfile || null,
  //                 },
  //               };
  //             }
  //             return state;
  //           });
  //         }
  //       },
  //       isAuthenticated: () => {
  //         return myApi.isAuthenticated();
  //       },
  //       authenticateWithBackend: async (firebaseUser: User) => {
  //         set((state) => ({
  //           ...state,
  //           auth: { ...state.auth, isLoading: true },
  //         }));

  //         try {
  //           const result = await myApi.authenticateWithBackend(firebaseUser);

  //           if (result.success) {
  //             const authData = myApi.getAuthData();
  //             if (authData?.user) {
  //               set((state) => ({
  //                 ...state,
  //                 auth: {
  //                   ...state.auth,
  //                   user: authData.user!,
  //                 },
  //               }));
  //             } else {
  //               set((state) => ({
  //                 ...state,
  //                 auth: { ...state.auth, user: null },
  //               }));
  //             }
  //           } else {
  //             throw new Error(result.error);
  //           }
  //         } catch (error) {
  //           console.error("Backend authentication failed:", error);
  //           set((state) => ({
  //             ...state,
  //             auth: { ...state.auth, isLoading: false },
  //           }));
  //           throw error;
  //         }
  //       },
  //     },
  //   };
  // }
  persist<AuthState>(
    (set) => ({
      token: null,
      profile: null,
      isAuth: false,
      errors: null,
      setToken: (token: string) =>
        set((state) => ({
          token,
          isAuth: !!token,
        })),
      register: async (user: createUser) => {
        try {
          const resRegister = await registerRequest(user);
          set(() => ({
            token: resRegister.data.token,
            isAuth: true,
          }));
        } catch (error) {
          set(() => ({ errors: error.response.data }));
        }
      },
      getProfile: async () => {
        const resProfile = await profileRequest();
        set(() => ({
          profile: resProfile.data,
        }));
      },
      logout: () => set(() => ({ token: null, profile: null, isAuth: false })),
      cleanErrors: () => set(() => ({ errors: null })),
    }),
    {
      name: "auth",
    }
  )
);
