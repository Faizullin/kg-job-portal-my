import { createFileRoute } from "@tanstack/react-router";
import { SupportFAQManagement } from "@/features/core/support-faq";

export const Route = createFileRoute("/_authenticated/core/faq")({
  component: SupportFAQManagement,
});
