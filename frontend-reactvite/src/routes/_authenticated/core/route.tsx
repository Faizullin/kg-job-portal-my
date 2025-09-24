import { AuthenticatedLayout } from "@/components/layout/authenticated-layout";
import { AuthClient } from "@/lib/auth/auth-client";
import { createFileRoute, redirect } from "@tanstack/react-router";

// Admin permission check function
const isAdmin = (): boolean => {
  const user = AuthClient.getCurrentUser();
  return user?.is_staff || user?.is_superuser || false;
};

export const Route = createFileRoute("/_authenticated/core")({
  component: AuthenticatedLayout,
  beforeLoad: async () => {
    if (!isAdmin()) {
      throw redirect({
        to: "/403",
        search: { redirect: window.location.pathname },
      });
    }
  },
});
