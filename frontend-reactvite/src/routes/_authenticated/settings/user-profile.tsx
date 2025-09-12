import { createFileRoute } from "@tanstack/react-router";
import { SettingsUserProfile } from "@/features/settings/user-profile";

export const Route = createFileRoute("/_authenticated/settings/user-profile")({
  component: SettingsUserProfile,
});


