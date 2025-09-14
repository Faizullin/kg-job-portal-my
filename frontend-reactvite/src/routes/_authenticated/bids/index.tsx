import { createFileRoute } from "@tanstack/react-router";
import { BidsList } from "@/features/bids/bids-list";
import { AuthClient } from "@/lib/auth/auth-client";

export const Route = createFileRoute("/_authenticated/bids/")({
  component: BidsPage,
});

function BidsPage() {
  const role = AuthClient.getCurrentUser()?.user_role || "client";
  const isProvider = /provider/i.test(role);
  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">{isProvider ? 'My Applications (Bids)' : 'Incoming Applications (Bids)'}</h2>
      </div>
      <BidsList />
    </div>
  );
}