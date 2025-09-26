import { ProfileTypeSelectionPage } from "@/features/app/profile-type-selection-page";
import { useAuthStore } from "@/stores/auth-store";
import { createFileRoute, redirect } from "@tanstack/react-router";


export const Route = createFileRoute("/_authenticated/")({
  beforeLoad: () => {
    const authStore = useAuthStore.getState();
    const { currentProfileType } = authStore;
    if (currentProfileType === 'service_provider') {
      throw redirect({ to: "/app/master" });
    } else if (currentProfileType === 'client') {
      throw redirect({ to: "/app/client" });
    }
    return;
  },
  component: ProfileTypeSelectionPage,
});
