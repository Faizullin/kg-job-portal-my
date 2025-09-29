import { ContentSection } from "../_components/content-section";
import { MasterForm } from "./master-form";
import myApi from "@/lib/api/my-api";
import { Button } from "@/components/ui/button";
import { useMutation, useQuery } from "@tanstack/react-query";

const loadMasterProfileQueryKey = "master-profile";

export function SettingsMaster() {
  const submitMutation = useMutation({
    mutationFn: async () => {
      await myApi.v1UsersMyMasterCreateCreate();
    },
    onSuccess: () => {
      window.location.reload();
    }
  });
  const loadMasterProfileQuery = useQuery({
    queryKey: [loadMasterProfileQueryKey],
    queryFn: async () => {
      try {
        const res = await myApi.v1UsersMyMasterRetrieve();
        return { exists: true, data: res.data } as const;
      } catch {
        return { exists: false } as const;
      }
    }
  });
  const masterProfileExists = loadMasterProfileQuery.data && loadMasterProfileQuery.data.exists;
  return (
    <ContentSection
      title="Master Profile"
      desc="Manage your service provider information and settings."
    >
      {!masterProfileExists ? (
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
        <MasterForm />
      )}
    </ContentSection>
  );
}
