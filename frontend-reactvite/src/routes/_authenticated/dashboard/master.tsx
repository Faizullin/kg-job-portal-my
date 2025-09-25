import { createFileRoute } from "@tanstack/react-router";
import { MasterDashboard } from "@/features/dashboard/components/master-dashboard";

export const Route = createFileRoute("/_authenticated/dashboard/master")({
  component: MasterDashboard,
});
