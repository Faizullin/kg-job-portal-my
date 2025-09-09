import { ContentSection } from "../_components/content-section";
import { ServiceProviderForm } from "./service-provider-form";

export function SettingsServiceProvider() {
  return (
    <ContentSection
      title="Service Provider Profile"
      desc="Manage your service provider information and settings."
    >
      <ServiceProviderForm />
    </ContentSection>
  );
}
