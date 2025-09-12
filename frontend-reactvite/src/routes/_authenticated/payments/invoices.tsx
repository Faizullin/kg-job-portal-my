import { createFileRoute } from "@tanstack/react-router";
import { InvoicesList } from "@/features/payments/invoices-list";

export const Route = createFileRoute("/_authenticated/payments/invoices")({
  component: InvoicesPage,
});

function InvoicesPage() {
  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Invoices</h2>
      </div>
      <InvoicesList />
    </div>
  );
}