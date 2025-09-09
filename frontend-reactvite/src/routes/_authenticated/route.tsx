import { AuthenticatedLayout } from "@/components/layout/authenticated-layout";
import { AuthClient } from "@/lib/auth/auth-client";
import { createFileRoute, redirect } from "@tanstack/react-router";

// Authentication check function
const isLoggedIn = (): boolean => {
  return AuthClient.isAuthenticated();
};

export const Route = createFileRoute("/_authenticated")({
  component: AuthenticatedLayout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/sign-in",
        search: { redirect: window.location.pathname },
      });
    }
  },
});
