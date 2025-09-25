import { createFileRoute } from "@tanstack/react-router";
import { ClientDashboard } from "@/features/dashboard/components/client-dashboard";

export const Route = createFileRoute("/_authenticated/dashboard/client")({
  component: ClientDashboard,
});
