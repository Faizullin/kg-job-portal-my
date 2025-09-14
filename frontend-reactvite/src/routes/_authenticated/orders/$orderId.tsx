import { createFileRoute } from "@tanstack/react-router";
import { OrderDetail } from "@/features/orders/order-detail";
import { AuthClient } from "@/lib/auth/auth-client";

export const Route = createFileRoute("/_authenticated/orders/$orderId")({
  component: OrderDetailPage,
});

function OrderDetailPage() {
  const { orderId } = Route.useParams();
  const role = AuthClient.getCurrentUser()?.user_role || "client";
  const isProvider = /provider/i.test(role);
  
  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">{isProvider ? 'Job Details' : 'Order Details'}</h2>
      </div>
      <OrderDetail orderId={orderId} />
    </div>
  );
}