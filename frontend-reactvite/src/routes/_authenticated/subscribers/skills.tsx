import { createFileRoute } from "@tanstack/react-router";
import { SkillsPage } from "@/features/subscribers/skills";

export const Route = createFileRoute("/_authenticated/subscribers/skills")({
  component: SkillsPage,
});