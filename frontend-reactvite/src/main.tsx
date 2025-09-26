import { QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createRouter, RouterProvider } from "@tanstack/react-router";
import { AxiosError } from "axios";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { toast } from "sonner";
import { DirectionProvider } from "./context/direction-provider";
import { FontProvider } from "./context/font-provider";
import { ThemeProvider } from "./context/theme-provider";
import { handleServerError } from "./lib/handle-server-error";
import { routeTree } from "./routeTree.gen";
import { useAuthStore } from "./stores/auth-store";

import "./styles/index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        if (import.meta.env.DEV) console.log({ failureCount, error });

        if (failureCount >= 0 && import.meta.env.DEV) return false;
        if (failureCount > 3 && import.meta.env.PROD) return false;

        return !(
          error instanceof AxiosError &&
          [401, 403].includes(error.response?.status ?? 0)
        );
      },
      refetchOnWindowFocus: import.meta.env.PROD,
      staleTime: 10 * 1000, // 10s
    },
    mutations: {
      onError: (error) => {
        handleServerError(error);

        if (error instanceof AxiosError) {
          if (error.response?.status === 304) {
            toast.error("Content not modified!");
          }
        }
      },
    },
  },
  queryCache: new QueryCache({
    onError: (error) => {
      if (error instanceof AxiosError) {
        if (error.response?.status === 401) {
          toast.error("Session expired!");
          useAuthStore.getState().reset();
          const redirect = `${router.history.location.href}`;
          router.navigate({ to: "/sign-in", search: { redirect } });
        }
        if (error.response?.status === 500) {
          toast.error("Internal Server Error!");
          // router.navigate({ to: "/500" });
        }
        if (error.response?.status === 403) {
          // router.navigate("/forbidden", { replace: true });
        }
      }
    },
  }),
});

// Create a new router instance
const router = createRouter({
  routeTree,
  context: { queryClient },
  defaultPreload: "intent",
  defaultPreloadStaleTime: 0,
  // basepath: import.meta.env.VITE_APP_BASE_URL,
});

// Register the router instance for type safety
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
        <FontProvider>
          <DirectionProvider>
            <RouterProvider router={router} />
          </DirectionProvider>
        </FontProvider>
      </ThemeProvider>
    </QueryClientProvider>
  </StrictMode>
);