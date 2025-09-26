import { createFileRoute } from "@tanstack/react-router";
import { MasterDashboard } from "@/features/app/components/master-dashboard";

export const Route = createFileRoute("/_authenticated/app/master")({
  component: MasterDashboard,
});
