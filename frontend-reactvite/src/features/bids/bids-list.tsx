import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";
import myApi from "@/lib/api/my-api";

export function BidsList() {
  const { data, isLoading } = useQuery({
    queryKey: ['bids'],
    queryFn: async () => myApi.v1OrdersBidsList({ page: 1, pageSize: 20 }).then(r => r.data),
    staleTime: 60_000,
  });

  const bids = (data as any)?.results || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'accepted': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'withdrawn': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return <div>Loading bids...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">All Bids</h3>
      </div>
      
      <div className="grid gap-4">
        {bids?.map((bid: any) => (
          <Card key={bid.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">Order #{bid.order}</CardTitle>
                  <CardDescription>by {bid.provider_name || 'Provider'}</CardDescription>
                </div>
                <Badge className={getStatusColor(bid.status)}>
                  {bid.status.toUpperCase()}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">{bid.description}</p>
                <div className="flex justify-between items-center">
                  <div className="space-y-1">
                    <p className="text-lg font-semibold">${bid.amount}</p>
                    {bid.estimated_duration ? (
                      <p className="text-sm text-muted-foreground">Est. {bid.estimated_duration} hours</p>
                    ) : null}
                    {bid.created_at ? (
                      <p className="text-sm text-muted-foreground">{new Date(bid.created_at).toLocaleDateString()}</p>
                    ) : null}
                  </div>
                  <div className="space-x-2">
                    <Button variant="outline" size="sm">
                      View Order
                    </Button>
                    {bid.status === 'pending' && (
                      <>
                        <Button size="sm" variant="outline">
                          Reject
                        </Button>
                        <Button size="sm">
                          Accept
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

