import { createFileRoute } from "@tanstack/react-router";
import { ServiceCategoriesManagement } from "@/features/core/service-categories";

export const Route = createFileRoute("/_authenticated/core/categories")({
  component: ServiceCategoriesManagement,
});
