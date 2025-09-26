import { NavigationProgress } from "@/components/navigation-progress";
import NiceModal from "@/components/nice-modal/modal-context";
import { Toaster } from "@/components/ui/sonner";
import { GeneralError } from "@/features/errors/general-error";
import { NotFoundError } from "@/features/errors/not-found-error";
import { type QueryClient } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { createRootRouteWithContext, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";


function RootComponent() {
  return (
    <>
      <NavigationProgress />
      <NiceModal.Provider>
        <Outlet />
      </NiceModal.Provider>
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
