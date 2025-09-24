import { createFileRoute } from "@tanstack/react-router";
import { ServiceAreasManagement } from "@/features/core/service-areas";

export const Route = createFileRoute("/_authenticated/core/areas")({
  component: ServiceAreasManagement,
});
