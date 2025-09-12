import { createFileRoute } from "@tanstack/react-router";
import { PaymentsList } from "@/features/payments/payments-list";

export const Route = createFileRoute("/_authenticated/payments/")({
  component: PaymentsPage,
});

function PaymentsPage() {
  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Payments</h2>
      </div>
      <PaymentsList />
    </div>
  );
}