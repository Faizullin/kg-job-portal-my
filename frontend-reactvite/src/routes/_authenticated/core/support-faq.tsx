import { createFileRoute } from "@tanstack/react-router";
import { SupportFAQManagement } from "@/features/core/support-faq";

export const Route = createFileRoute("/_authenticated/core/support-faq")({
  component: SupportFAQManagement,
});
