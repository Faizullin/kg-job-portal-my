import { createFileRoute } from "@tanstack/react-router";
import { SystemSettingsManagement } from "@/features/core/system-settings";

export const Route = createFileRoute("/_authenticated/core/system-settings")({
  component: SystemSettingsManagement,
});
