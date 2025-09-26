import { AuthenticatedLayout } from "@/components/layout/authenticated-layout";
import myApi from "@/lib/api/my-api";
import { useAuthStore } from "@/stores/auth-store";
import { queryOptions } from "@tanstack/react-query";
import { createFileRoute, redirect } from "@tanstack/react-router";

const userProfileQueryKey = "user-profile";

const userProfileQueryOptions = () =>
  queryOptions({
    queryKey: [userProfileQueryKey],
    queryFn: async () => {
      const response = await myApi.v1ProfileRetrieve();
      return response.data;
    },
  });


const LoadingPage = () => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h1>Loading...</h1>
  </div>
);

export const Route = createFileRoute("/_authenticated")({
  component: AuthenticatedLayout,
  pendingComponent: LoadingPage,
  beforeLoad: async ({ context }) => {
    const auth = useAuthStore.getState();
    if (auth.isAuthenticated) {
      try {
        const response = await context.queryClient.ensureQueryData(userProfileQueryOptions());
        if (auth.currentProfileType === null) {
          if (response.groups.includes('client')) {
            auth.setCurrentProfileType('client');
          } else if (response.groups.includes('service_provider')) {
            auth.setCurrentProfileType('service_provider');
          }
        }
      } catch (error) {
        if (!auth.isAuthenticated) {
          throw redirect({
            to: "/sign-in",
            search: { redirect: window.location.pathname },
          });
        }
        console.error("Failed to load user profile:", error);
        throw error;
      }
    } else {
      throw redirect({
        to: "/sign-in",
        search: { redirect: window.location.pathname },
      });
    }
  },
});
