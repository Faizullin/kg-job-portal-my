import { NavigationProgress } from "@/components/navigation-progress";
import { Toaster } from "@/components/ui/sonner";
import { GeneralError } from "@/features/errors/general-error";
import { NotFoundError } from "@/features/errors/not-found-error";
import { useAuthStore } from "@/stores/auth-store";
import { type QueryClient } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { createRootRouteWithContext, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { useEffect } from "react";

function RootComponent() {
  // Load authentication state from localStorage on initial load
  useEffect(() => {
    const { auth } = useAuthStore.getState();
    auth.loadFromStorage();
  }, []); // Empty dependency array to run only once o             n mount

  return (
    <>
      <NavigationProgress />
      <Outlet />
      <Toaster duration={5000} />
      {import.meta.env.MODE === "development" && (
        <>
          <ReactQueryDevtools buttonPosition="bottom-left" />
          <TanStackRouterDevtools position="bottom-right" />
        </>
      )}
    </>
  );
}

export const Route = createRootRouteWithContext<{
  queryClient: QueryClient;
}>()({
  component: RootComponent,
  notFoundComponent: NotFoundError,
  errorComponent: GeneralError,
});
