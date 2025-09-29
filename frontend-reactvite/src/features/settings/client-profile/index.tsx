import { Button } from "@/components/ui/button";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ContentSection } from "../_components/content-section";
import { ClientProfileForm } from "./client-profile-form";

const loadClientProfileQueryKey = "client-profile";

export function SettingsClientProfile() {
  const submitMutation = useMutation({
    mutationFn: async () => {
      await myApi.v1UsersMyEmployerCreateCreate();
    },
    onSuccess: () => {
      window.location.reload();
    }
  });
  const loadClientProfileQuery = useQuery({
    queryKey: [loadClientProfileQueryKey],
    queryFn: async () => {
      try {
        const res = await myApi.v1UsersMyEmployerRetrieve();
        return { exists: true, data: res.data };
      } catch {
        return { exists: false };
      }
    }
  });
  const clientProfileExists = loadClientProfileQuery.data && loadClientProfileQuery.data.exists;
  return (
    <ContentSection
      title="Client Profile"
      desc="Manage your client preferences and settings."
    >
      {!clientProfileExists ? (
        <div className="flex items-center justify-between rounded-md border p-4">
          <div>
            <div className="font-medium">No client profile found</div>
            <div className="text-sm text-muted-foreground">Initialize a client profile to enable client-specific settings.</div>
          </div>
          <Button
            disabled={submitMutation.isPending}
            onClick={() => submitMutation.mutate()}
          >
            Initialize
          </Button>
        </div>
      ) : (
        <ClientProfileForm />
      )}
    </ContentSection>
  );
}
