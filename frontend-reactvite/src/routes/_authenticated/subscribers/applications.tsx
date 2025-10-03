import { createFileRoute } from "@tanstack/react-router";
import { ApplicationsPage } from "@/features/subscribers/applications";

export const Route = createFileRoute("/_authenticated/subscribers/applications")({
  component: ApplicationsPageComponent,
});

function ApplicationsPageComponent() {
  return <ApplicationsPage />;
}