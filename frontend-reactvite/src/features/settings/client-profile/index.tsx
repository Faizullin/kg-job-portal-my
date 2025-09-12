import { ContentSection } from "../_components/content-section";
import { ClientProfileForm } from "./client-profile-form";
import myApi from "@/lib/api/my-api";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";

export function SettingsClientProfile() {
  const { data, isLoading } = useQuery({
    queryKey: ["client-profile-init-check"],
    queryFn: async () => {
      try {
        const res = await myApi.v1UsersClientRetrieve();
        return { exists: true, data: res.data } as const;
      } catch {
        return { exists: false } as const;
      }
    }
  });

  return (
    <ContentSection
      title="Client Profile"
      desc="Manage your client preferences and settings."
    >
      {!isLoading && data && !data.exists ? (
        <div className="flex items-center justify-between rounded-md border p-4">
          <div>
            <div className="font-medium">No client profile found</div>
            <div className="text-sm text-muted-foreground">Initialize a client profile to enable client-specific settings.</div>
          </div>
          <Button
            onClick={async () => {
              await myApi.v1UsersClientUpdateCreate();
              window.location.reload();
            }}
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
