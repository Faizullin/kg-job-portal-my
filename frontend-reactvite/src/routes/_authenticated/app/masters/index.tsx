import { createFileRoute } from "@tanstack/react-router";
import { MastersPage } from "@/features/app/masters/masters-page";

export const Route = createFileRoute("/_authenticated/app/masters/")({
  component: MastersPage,
});