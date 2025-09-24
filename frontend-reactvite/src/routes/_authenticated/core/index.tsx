import { createFileRoute } from "@tanstack/react-router";
import { AdminDashboard } from "@/features/core";

export const Route = createFileRoute("/_authenticated/core/")({
  component: AdminDashboard,
});
