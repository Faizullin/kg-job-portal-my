import { ContentSection } from "../_components/content-section";
import { ClientProfileForm } from "./client-profile-form";

export function SettingsClientProfile() {
  return (
    <ContentSection
      title="Client Profile"
      desc="Manage your client preferences and settings."
    >
      <ClientProfileForm />
    </ContentSection>
  );
}
