import { createFileRoute } from "@tanstack/react-router";
import { SystemSettingsManagement } from "@/features/core/system-settings";

export const Route = createFileRoute("/_authenticated/core/settings")({
  component: SystemSettingsManagement,
});
