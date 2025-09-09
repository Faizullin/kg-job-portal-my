import { createFileRoute } from "@tanstack/react-router";
import { SettingsClientProfile } from "@/features/settings/client-profile";

export const Route = createFileRoute("/_authenticated/settings/client-profile")({
  component: SettingsClientProfile,
});