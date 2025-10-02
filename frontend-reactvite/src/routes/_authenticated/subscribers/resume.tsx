import { createFileRoute } from "@tanstack/react-router";
import { ResumePage } from "@/features/subscribers/resume";

export const Route = createFileRoute("/_authenticated/subscribers/resume")({
  component: ResumePage,
});