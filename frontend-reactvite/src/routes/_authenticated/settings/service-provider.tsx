import { createFileRoute } from "@tanstack/react-router";
import { SettingsServiceProvider } from "@/features/settings/service-provider";

export const Route = createFileRoute("/_authenticated/settings/service-provider")({
  component: SettingsServiceProvider,
});