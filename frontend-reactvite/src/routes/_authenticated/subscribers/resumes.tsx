import { createFileRoute } from "@tanstack/react-router";
import { ResumesPage } from "@/features/subscribers/resume";

export const Route = createFileRoute("/_authenticated/subscribers/resumes")({
  component: ResumesPage,
});