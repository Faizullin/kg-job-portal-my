import { createFileRoute } from "@tanstack/react-router";
import { MasterDetailsPage } from "@/features/app/service-providers/master-details-page";

export const Route = createFileRoute("/_authenticated/app/service-providers/$providerId")({
  component: ServiceProviderDetailPage,
});

function ServiceProviderDetailPage() {
  const { providerId } = Route.useParams();
  
  return <MasterDetailsPage providerId={providerId} />;
}