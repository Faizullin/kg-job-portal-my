import { createFileRoute } from "@tanstack/react-router";
import { ServiceProvidersList } from "@/features/service-providers/service-providers-list";

export const Route = createFileRoute("/_authenticated/service-providers/")({
  component: ServiceProvidersPage,
});

function ServiceProvidersPage() {
  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Service Providers</h2>
      </div>
      <ServiceProvidersList />
    </div>
  );
}