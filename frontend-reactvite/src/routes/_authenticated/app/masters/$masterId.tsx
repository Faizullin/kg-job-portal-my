import { createFileRoute } from "@tanstack/react-router";
import { MasterDetailsPage } from "@/features/app/masters/master-details-page";

export const Route = createFileRoute("/_authenticated/app/masters/$masterId")({
  component: ServiceProviderDetailPage,
});

function ServiceProviderDetailPage() {
  const { masterId } = Route.useParams();
  
  return <MasterDetailsPage masterId={masterId} />;
}