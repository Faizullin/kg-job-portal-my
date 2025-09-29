import { SettingsMaster } from "@/features/settings/master";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/settings/master")({
  component: SettingsMaster,
});