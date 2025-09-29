import { JobDetail } from "@/features/jobs/order-detail";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/jobs/$jobId")({
  component: JobDetailPage,
});

function JobDetailPage() {
  const { jobId } = Route.useParams();

  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Job Details</h2>
      </div>
      <JobDetail jobId={jobId} />
    </div>
  );
}