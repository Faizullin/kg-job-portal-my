import { createFileRoute } from "@tanstack/react-router";
import { EmployerApplicationsPage } from "@/features/employer/applications";

export const Route = createFileRoute("/_authenticated/employer/applications")({
  component: EmployerApplicationsPageComponent,
});

function EmployerApplicationsPageComponent() {
  return <EmployerApplicationsPage />;
}