import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useDialogControl } from "@/hooks/use-dialog-control";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BidCreateEditDialog, type BidFormData } from "./components/bid-create-edit-dialog";
import { useAuthStore } from "@/stores/auth-store";
import { useMemo } from "react";

const loadJobRetrieveQueryKey = "jobs"

interface JobDetailProps {
  jobId : string;
}

export function JobDetail({ jobId }: JobDetailProps) {
  const auth = useAuthStore();
  const bidDialog = useDialogControl<BidFormData>();

  const queryClient = useQueryClient();

  const { data: job, isLoading } = useQuery({
    queryKey: [loadJobRetrieveQueryKey, jobId],
    queryFn: async () => {
      const response = await myApi.v1JobsRetrieve({ id: Number(jobId) })
      return response.data;
    },
    staleTime: 60_000,
  });

  // Dialog handlers
  const handleCreateBid = () => {
    bidDialog.show({
      order_id: parseInt(jobId),
      amount: 0,
      description: "",
      estimated_duration: 0,
      terms_conditions: "",
      is_negotiable: false
    });
  };

  const handleEditBid = (bid: any) => {
    bidDialog.show({
      id: bid.id,
      order_id: parseInt(jobId),
      amount: bid.amount,
      description: bid.description,
      estimated_duration: 4,
      terms_conditions: "",
      is_negotiable: false
    });
  };

  const bidMutation = useMutation({
    mutationFn: async (payload: BidFormData) => {
      return myApi.v1JobsBidsCreateOrUpdate({
        jobId: Number(jobId),
        bidCreateOrUpdate: {
          amount: String(payload.amount),
          description: payload.description,
          estimated_duration: payload.estimated_duration,
          terms_conditions: payload.terms_conditions || "",
          is_negotiable: payload.is_negotiable,
        },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadJobRetrieveQueryKey, jobId] });
    }
  });

  const handleSaveBid = (data: BidFormData) => {
    bidMutation.mutate(data);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return <div>Loading order details...</div>;
  }

  const userRole = useMemo(() => {
    return auth.user?.user_role || "client";
  }, [auth.user]);
  const isProvider = /provider/i.test(userRole);

  const bids = (job as any)?.bids || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-2xl font-bold">{job?.title}</h3>
          <p className="text-muted-foreground">Order #{job?.id}</p>
        </div>
        <Badge className={getStatusColor(job?.status || '')}>
          {job?.status?.replace('_', ' ').toUpperCase()}
        </Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Order Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-medium">Description</h4>
              <p className="text-sm text-muted-foreground">{job?.description}</p>
            </div>
            <div>
              <h4 className="font-medium">Service Subcategory</h4>
              <p className="text-sm text-muted-foreground">{String(job?.service_subcategory)}</p>
            </div>
            <div>
              <h4 className="font-medium">Location</h4>
              <p className="text-sm text-muted-foreground">{job?.location}</p>
            </div>
            <div>
              <h4 className="font-medium">Service Date & Time</h4>
              <p className="text-sm text-muted-foreground">
                {job?.service_date} at {job?.service_time}
              </p>
            </div>
            <div>
              <h4 className="font-medium">Budget Range</h4>
              <p className="text-sm text-muted-foreground">
                  ${job?.budget_min} - ${job?.budget_max}
              </p>
            </div>
            {job?.special_requirements && (
              <div>
                <h4 className="font-medium">Special Requirements</h4>
                <p className="text-sm text-muted-foreground">{job.special_requirements}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {!isProvider && (
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Bids ({bids.length})</CardTitle>
                  <CardDescription>Service provider bids on this job</CardDescription>
                </div>
                <div />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {bids.map((bid: any) => (
                  <div key={bid.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium">{bid.provider_name}</h4>
                      <Badge variant="outline">{bid.status}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{bid.description}</p>
                    <div className="flex justify-between items-center">
                      <span className="text-lg font-semibold">${bid.amount}</span>
                      <div className="space-x-2">
                        <Button size="sm" variant="outline">View Profile</Button>
                        <Button size="sm" variant="outline" onClick={() => handleEditBid(bid)}>
                          Edit Bid
                        </Button>
                        <Button size="sm">Accept Bid</Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {isProvider && (
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Your Bid</CardTitle>
                  <CardDescription>Submit or update your bid</CardDescription>
                </div>
                <Button onClick={handleCreateBid} disabled={bidMutation.isPending}>
                  {bidMutation.isPending ? "Submitting..." : "Submit Bid"}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">
                After submission, the client will review and may contact you.
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Dialogs */}
      <BidCreateEditDialog
        control={bidDialog}
        onSave={handleSaveBid}
      />
    </div>
  );
}
