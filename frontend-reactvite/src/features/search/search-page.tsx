import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useDialogControl } from "@/hooks/use-dialog-control";
import type { Order } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Calendar, DollarSign, MapPin, Search as SearchIcon } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { Link } from "@tanstack/react-router";
import { BidCreateEditDialog, type BidFormData } from "@/features/orders/components/bid-create-edit-dialog";

export function SearchPage() {
  const [q, setQ] = useState("");
  const [city, setCity] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const bidDialog = useDialogControl<BidFormData>();
  const queryClient = useQueryClient();

  const ordersQuery = useQuery({
    queryKey: ["search-orders", { q, city, page, pageSize }],
    queryFn: () =>
      myApi
        .v1SearchOrdersList({
          q: q || undefined,
          city: city || undefined,
          page,
          pageSize,
          ordering: "-created_at",
        })
        .then((r) => r.data),
    placeholderData: (prev) => prev,
    staleTime: 60_000,
  });

  const orders: Order[] = useMemo(() => {
    const data: any = ordersQuery.data;
    if (!data) return [];
    if (Array.isArray(data.results)) return data.results as Order[];
    if (Array.isArray((data as any).results?.results)) return (data as any).results.results as Order[];
    return [];
  }, [ordersQuery.data]);

  const totalCount = useMemo(() => {
    const data: any = ordersQuery.data;
    return (data?.count as number) || (data?.results?.count as number) || orders.length;
  }, [ordersQuery.data, orders.length]);

  const bidMutation = useMutation({
    mutationFn: async (payload: BidFormData) => {
      return myApi.v1OrdersBidsCreate({
        orderId: payload.order_id,
        bidCreate: {
          amount: String(payload.amount),
          description: payload.description,
          estimated_duration: payload.estimated_duration,
          terms_conditions: payload.terms_conditions || "",
          is_negotiable: payload.is_negotiable,
        },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["search-orders"] });
    },
  });

  const handleOpenBid = useCallback(
    (order: Order) => {
      bidDialog.show({
        order_id: Number(order.id),
        amount: 0,
        description: "",
        estimated_duration: 1,
        terms_conditions: "",
        is_negotiable: false,
      });
    },
    [bidDialog]
  );

  const handleSaveBid = useCallback(
    (data: BidFormData) => {
      bidMutation.mutate(data);
    },
    [bidMutation]
  );

  const getStatusColor = useCallback((status: string) => {
    switch (status) {
      case "published":
        return "bg-blue-100 text-blue-800";
      case "bidding":
        return "bg-purple-100 text-purple-800";
      case "in_progress":
        return "bg-yellow-100 text-yellow-800";
      case "completed":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  }, []);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Find Jobs</CardTitle>
          <CardDescription>Search and apply for open orders</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative flex-1 min-w-[220px]">
              <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by title, description, location"
                value={q}
                onChange={(e) => {
                  setQ(e.target.value);
                  setPage(1);
                }}
                className="pl-8 h-9"
              />
            </div>
            <div className="relative w-full sm:w-64">
              <MapPin className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="City (optional)"
                value={city}
                onChange={(e) => {
                  setCity(e.target.value);
                  setPage(1);
                }}
                className="pl-8 h-9"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4">
        {ordersQuery.isLoading && (
          <div className="text-sm text-muted-foreground">Loading jobs...</div>
        )}
        {!ordersQuery.isLoading && orders.length === 0 && (
          <div className="text-sm text-muted-foreground">No jobs found</div>
        )}

        {orders.map((order) => (
          <Card key={order.id}>
            <CardHeader className="flex flex-row items-start justify-between gap-4">
              <div>
                <CardTitle className="text-base">{order.title}</CardTitle>
                <CardDescription className="mt-1 line-clamp-2">
                  {order.description}
                </CardDescription>
              </div>
              <Badge className={getStatusColor((order as any).status || "published")}>
                {String((order as any).status || "published").replace("_", " ").toUpperCase()}
              </Badge>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1"><Calendar className="h-3 w-3" />{order.service_date || "Flexible"}</span>
                <span className="flex items-center gap-1"><DollarSign className="h-3 w-3" />{order.budget_min ? `${order.budget_min}` : "-"}{order.budget_max ? ` - ${order.budget_max}` : ""}</span>
                <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{order.city}</span>
              </div>
              <div className="flex gap-2">
                <Button asChild variant="outline">
                  <Link to="/orders/$orderId" params={{ orderId: String(order.id) }}>View Details</Link>
                </Button>
                <Button onClick={() => handleOpenBid(order)} disabled={bidMutation.isPending}>
                  {bidMutation.isPending ? "Submitting..." : "Apply / Submit Bid"}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}

        {totalCount > pageSize && (
          <div className="flex items-center justify-between pt-2">
            <div className="text-sm text-muted-foreground">{totalCount} jobs</div>
            <div className="flex gap-2">
              <Button variant="outline" disabled={page === 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>Prev</Button>
              <Button variant="outline" disabled={orders.length < pageSize} onClick={() => setPage((p) => p + 1)}>Next</Button>
            </div>
          </div>
        )}
      </div>

      <BidCreateEditDialog control={bidDialog} onSave={handleSaveBid} />
    </div>
  );
}


