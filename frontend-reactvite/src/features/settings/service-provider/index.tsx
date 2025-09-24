import { ContentSection } from "../_components/content-section";
import { ServiceProviderForm } from "./service-provider-form";
import myApi from "@/lib/api/my-api";
import { Button } from "@/components/ui/button";
import { useMutation, useQuery } from "@tanstack/react-query";

const loadProviderProfileQueryKey = "provider-profile";

export function SettingsServiceProvider() {
  const submitMutation = useMutation({
    mutationFn: async () => {
      await myApi.v1UsersProviderCreateCreate();
    },
    onSuccess: () => {
      window.location.reload();
    }
  });
  const loadProviderProfileQuery = useQuery({
    queryKey: [loadProviderProfileQueryKey],
    queryFn: async () => {
      try {
        const res = await myApi.v1UsersProviderRetrieve();
        return { exists: true, data: res.data } as const;
      } catch {
        return { exists: false } as const;
      }
    }
  });
  const providerProfileExists = loadProviderProfileQuery.data && loadProviderProfileQuery.data.exists;
  return (
    <ContentSection
      title="Service Provider Profile"
      desc="Manage your service provider information and settings."
    >
      {!providerProfileExists ? (
        <div className="flex items-center justify-between rounded-md border p-4">
          <div>
            <div className="font-medium">No provider profile found</div>
            <div className="text-sm text-muted-foreground">Initialize a provider profile to enable provider-specific settings.</div>
          </div>
          <Button
            disabled={submitMutation.isPending}
            onClick={() => submitMutation.mutate()}
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
