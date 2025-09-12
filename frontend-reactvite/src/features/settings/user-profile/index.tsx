import { ContentSection } from "../_components/content-section";
import { UserProfileForm } from "./user-profile-form";


export function SettingsUserProfile() {
  return (
    <ContentSection
      title="User Profile"
      desc="Manage your extended user profile."
    >
      <UserProfileForm />
    </ContentSection>
  );
}


