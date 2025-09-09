import { createFileRoute } from "@tanstack/react-router";
import { SettingsExtendedProfile } from "@/features/settings/extended-profile";

export const Route = createFileRoute("/_authenticated/settings/extended-profile")({
  component: SettingsExtendedProfile,
});