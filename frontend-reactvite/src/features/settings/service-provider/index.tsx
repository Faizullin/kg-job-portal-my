import { ContentSection } from "../_components/content-section";
import { ServiceProviderForm } from "./service-provider-form";
import myApi from "@/lib/api/my-api";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";

export function SettingsServiceProvider() {
  const { data, isLoading } = useQuery({
    queryKey: ["provider-profile-init-check"],
    queryFn: async () => {
      try {
        const res = await myApi.v1UsersProviderRetrieve();
        return { exists: true, data: res.data } as const;
      } catch {
        return { exists: false } as const;
      }
    }
  });

  return (
    <ContentSection
      title="Service Provider Profile"
      desc="Manage your service provider information and settings."
    >
      {!isLoading && data && !data.exists ? (
        <div className="flex items-center justify-between rounded-md border p-4">
          <div>
            <div className="font-medium">No provider profile found</div>
            <div className="text-sm text-muted-foreground">Initialize a provider profile to enable provider-specific settings.</div>
          </div>
          <Button
            onClick={async () => {
              await myApi.v1UsersProviderUpdateCreate();
              window.location.reload();
            }}
          >
            Initialize
          </Button>
        </div>
      ) : (
        <ServiceProviderForm />
      )}
    </ContentSection>
  );
}
