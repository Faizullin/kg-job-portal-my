import { ContentSection } from "../_components/content-section";
import { ExtendedProfileForm } from "./extended-profile-form";

export function SettingsExtendedProfile() {
  return (
    <ContentSection
      title="Extended Profile"
      desc="Additional information about yourself."
    >
      <ExtendedProfileForm />
    </ContentSection>
  );
}
