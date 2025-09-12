import { createFileRoute } from "@tanstack/react-router";
import { ServiceProviderDetail } from "@/features/service-providers/service-provider-detail";

export const Route = createFileRoute("/_authenticated/service-providers/$providerId")({
  component: ServiceProviderDetailPage,
});

function ServiceProviderDetailPage() {
  const { providerId } = Route.useParams();
  
  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Service Provider</h2>
      </div>
      <ServiceProviderDetail providerId={providerId} />
    </div>
  );
}