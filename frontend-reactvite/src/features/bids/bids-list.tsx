import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";

export function BidsList() {
  const { data: bids, isLoading } = useQuery({
    queryKey: ['bids'],
    queryFn: async () => {
      // Mock data - replace with actual API call
      return [
        {
          id: 1,
          order_title: "House Cleaning Service",
          amount: 140,
          description: "Professional cleaning with eco-friendly products",
          status: "pending",
          provider_name: "CleanPro Services",
          created_at: "2024-01-16T08:00:00Z",
          estimated_duration: 4
        },
        {
          id: 2,
          order_title: "Plumbing Repair",
          amount: 80,
          description: "Quick fix for leaking faucet",
          status: "accepted",
          provider_name: "FixIt Plumbing",
          created_at: "2024-01-15T14:30:00Z",
          estimated_duration: 2
        },
        {
          id: 3,
          order_title: "Garden Maintenance",
          amount: 60,
          description: "Weekly lawn care and trimming",
          status: "rejected",
          provider_name: "Green Thumb Landscaping",
          created_at: "2024-01-14T10:15:00Z",
          estimated_duration: 3
        }
      ];
    }
  });

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
        {bids?.map((bid) => (
          <Card key={bid.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">{bid.order_title}</CardTitle>
                  <CardDescription>by {bid.provider_name}</CardDescription>
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
                    <p className="text-sm text-muted-foreground">
                      Est. {bid.estimated_duration} hours
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(bid.created_at).toLocaleDateString()}
                    </p>
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

