import { createFileRoute } from "@tanstack/react-router";
import { PortfolioPage } from "@/features/subscribers/portfolio";

export const Route = createFileRoute("/_authenticated/subscribers/portfolio")({
  component: PortfolioPage,
});