import { createFileRoute } from "@tanstack/react-router";
import { ClientDashboard } from "@/features/app/components/client-dashboard";

export const Route = createFileRoute("/_authenticated/app/client")({
  component: ClientDashboard,
});
