import { createFileRoute } from "@tanstack/react-router";
import { ServiceSubcategoriesManagement } from "@/features/core/service-subcategories";

export const Route = createFileRoute("/_authenticated/core/subcategories")({
  component: ServiceSubcategoriesManagement,
});
