import { createFileRoute } from "@tanstack/react-router";
import { ServiceCategoriesManagement } from "@/features/core/service-categories";

export const Route = createFileRoute("/_authenticated/core/service-categories")({
  component: ServiceCategoriesManagement,
});
