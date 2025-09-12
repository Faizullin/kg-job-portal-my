import type { UserProfile } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useQuery } from "@tanstack/react-query";
import { createContext, useContext } from "react";

type UserContextValue = { user: UserProfile | null; isLoading: boolean };
const UserContext = createContext<UserContextValue>({ user: null, isLoading: false });

export function FirebaseAuthProvider({ children }: { children: React.ReactNode }) {
  const { data, isLoading } = useQuery({
    queryKey: ["user-profile"],
    queryFn: () => myApi.v1ProfileRetrieve(),
    enabled: myApi.isAuthenticated(),
    select: (res) => res.data,
    staleTime: 5 * 60 * 1000,
  });

  return (
    <UserContext.Provider value={{ user: data ?? null, isLoading }}>
      {children}
    </UserContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useUser() {
  return useContext(UserContext);
}
