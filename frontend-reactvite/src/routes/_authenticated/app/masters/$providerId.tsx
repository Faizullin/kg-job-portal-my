import { createFileRoute } from "@tanstack/react-router";
import { MasterDetailsPage } from "@/features/app/masters/master-details-page";

export const Route = createFileRoute("/_authenticated/app/masters/$providerId")({
  component: ServiceProviderDetailPage,
});

function ServiceProviderDetailPage() {
  const { providerId } = Route.useParams();
  
  return <MasterDetailsPage providerId={providerId} />;
}