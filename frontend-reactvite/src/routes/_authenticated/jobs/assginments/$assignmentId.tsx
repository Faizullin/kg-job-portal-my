import { createFileRoute } from "@tanstack/react-router";
import { MasterAssignmentDetail } from "@/features/jobs/master-order-detail";

export const Route = createFileRoute("/_authenticated/jobs/assginments/$assignmentId")({
  component: MasterOrderDetailComponent,
});

function MasterOrderDetailComponent() {
  return <MasterAssignmentDetail />;
}