import { createFileRoute } from "@tanstack/react-router";
import { AnalyticsOverview } from "@/features/analytics/analytics-overview";

export const Route = createFileRoute("/_authenticated/analytics/")({
  component: AnalyticsPage,
});

function AnalyticsPage() {
  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Analytics</h2>
      </div>
      <AnalyticsOverview />
    </div>
  );
}