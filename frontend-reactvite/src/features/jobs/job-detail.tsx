import { AttachmentsView } from "@/components/attachments/attachments-view";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { Attachment, JobApplyRequest } from "@/lib/api/axios-client";
import myApi from "@/lib/api/my-api";
import { useAuthStore } from "@/stores/auth-store";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import {
  Calendar,
  CheckCircle,
  Clock,
  Map,
  MapPin,
  MessageCircle,
  Phone,
  Star
} from "lucide-react";
import { useCallback, useMemo } from "react";
import { toast } from "sonner";

interface JobDetailProps {
  jobId: string;
}

const JOB_DETAIL_QUERY_KEY = "job-detail";
const JOB_ATTACHMENTS_QUERY_KEY = "job-attachments";

export function JobDetail({ jobId }: JobDetailProps) {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const navigate = useNavigate();

  // Check if current user is a master
  const isMaster = useMemo(() => {
    return user?.groups?.includes('master') || false;
  }, [user?.groups]);

  // Fetch job details
  const jobQuery = useQuery({
    queryKey: [JOB_DETAIL_QUERY_KEY, jobId],
    queryFn: async () => {
      const response = await myApi.v1JobsRetrieve({ id: parseInt(jobId) });
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  // Fetch job attachments
  const attachmentsQuery = useQuery({
    queryKey: [JOB_ATTACHMENTS_QUERY_KEY, jobId],
    queryFn: async () => {
      const response = await myApi.v1JobsAttachmentsList({ jobId });
      return response.data.results || [];
    },
    staleTime: 5 * 60 * 1000,
    retry: 1,
    enabled: !!jobQuery.data, // Only load attachments after job details are loaded
  });

  // Format budget display
  const formatBudget = useCallback(() => {
    const job = jobQuery.data;
    if (job?.budget_min && job?.budget_max) {
      return `${job.budget_min} - ${job.budget_max} тг`;
    } else if (job?.budget_min) {
      return `${job.budget_min} тг`;
    } else if (job?.budget_max) {
      return `до ${job.budget_max} тг`;
    }
    return "Цена договорная";
  }, [jobQuery.data]);

  // Format service date
  const formatServiceDate = useCallback(() => {
    const job = jobQuery.data;
    if (job?.service_date) {
      const date = new Date(job.service_date);
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);

      if (date.toDateString() === tomorrow.toDateString()) {
        return `Завтра, ${job.service_time || "время не указано"}`;
      }
      return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
    return "Дата не указана";
  }, [jobQuery.data]);

  // Get customer initials
  const customerInitials = useMemo(() => {
    const job = jobQuery.data;
    const firstName = job?.employer?.user?.first_name || "";
    const lastName = job?.employer?.user?.last_name || "";
    const username = job?.employer?.user?.username || "";

    if (firstName && lastName) {
      return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
    } else if (username) {
      return username.charAt(0).toUpperCase();
    }
    return "AA";
  }, [jobQuery.data]);

  // Get customer rating and reviews from API data
  const customerRating = useMemo(() => {
    // For now using mock data, but could be extended to use job.employer statistics
    return 4.7;
  }, []);

  const customerReviews = useMemo(() => {
    // For now using mock data, but could be extended to use job.employer statistics
    return 25;
  }, []);

  // Apply to job mutation
  const applyJobMutation = useMutation({
    mutationFn: async (applicationData: JobApplyRequest) => {
      const response = await myApi.v1JobsApply({
        id: parseInt(jobId),
        jobApplyRequest: applicationData
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [JOB_DETAIL_QUERY_KEY, jobId] });
      toast.success("Application submitted successfully!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Failed to apply for job");
    },
  });

  const handleApplyToJob = useCallback(() => {
    if (jobQuery.data) {
      // For now, using basic application data
      // In a real app, you might want to show a dialog to collect amount, comment, etc.
      const applicationData: JobApplyRequest = {
        amount: jobQuery.data.budget_min || "0",
        comment: "I'm interested in this job",
        estimated_duration: null,
        resume: null
      };
      applyJobMutation.mutate(applicationData);
    }
  }, [jobQuery.data, applyJobMutation]);

  const handleCallCustomer = useCallback(() => {
    // In a real app, this would initiate a phone call
    toast.info("Calling customer...");
  }, []);

  // Find or create chat with job employer
  const findOrCreateChatMutation = useMutation({
    mutationFn: async () => {
      const job = jobQuery.data;
      if (!user || !job?.employer?.user) {
        throw new Error("User or employer not found");
      }

      // First try to find existing chat room with the master
      const roomsResponse = await myApi.v1ChatsRoomsForMaster({
        masterId: job.employer.user.id,
      });

      if (roomsResponse.data.length > 0) {
        return roomsResponse.data[0];
      }

      // If no existing chat, create a new one
      const response = await myApi.v1ChatsRoomsCreate({
        chatRoomCreateRequest: {
          title: `Чат по заказу: ${job.title}`,
          chat_type: "job_chat" as any,
          participants_users_ids: [user.id, job.employer.user.id],
          job: job.id,
        } as any
      });

      return response.data;
    },
    onSuccess: (chatRoom) => {
      // Navigate to the chat room using search params
      navigate({ to: '/chats', search: { chat_room_id: chatRoom.id } });
    },
    onError: (error) => {
      console.error("Error finding or creating chat:", error);
      toast.error("Failed to start chat");
    }
  });

  const handleMessageCustomer = useCallback(() => {
    findOrCreateChatMutation.mutate();
  }, [findOrCreateChatMutation]);

  const handleShowOnMap = useCallback(() => {
    // In a real app, this would open a map with the job location
    toast.info("Opening map...");
  }, []);

  // Attachment handlers
  const handleUploadAttachments = useCallback(async (files: File[]) => {
    try {
      await myApi.v1JobsAttachmentsCreate({
        jobId,
        files
      });
      return { success: true, files };
    } catch {
      return { success: false, files, error: "Failed to upload files" };
    }
  }, [jobId]);

  const handleDeleteAttachment = useCallback(async (attachment: Attachment) => {
    await myApi.v1JobsAttachmentsDestroy({
      id: attachment.id.toString(),
      jobId
    });
  }, [jobId]);

  const handleAttachmentUploadSuccess = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: [JOB_ATTACHMENTS_QUERY_KEY, jobId] });
  }, [queryClient, jobId]);

  const handleAttachmentDeleteSuccess = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: [JOB_ATTACHMENTS_QUERY_KEY, jobId] });
  }, [queryClient, jobId]);

  if (jobQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (jobQuery.error || !jobQuery.data) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading job details</p>
        <Button onClick={() => window.location.reload()} className="mt-2">
          Try Again
        </Button>
      </div>
    );
  }


  return (
    <div className="max-w-2xl mx-auto space-y-6 p-4">
      {/* Job Details Card */}
      <Card>
        <CardContent className="p-6 space-y-4">
          {/* Job Title */}
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{jobQuery.data?.title}</h1>
            <p className="text-gray-600 mt-2">{jobQuery.data?.description}</p>
          </div>

          {/* Price */}
          <div className="flex items-center justify-between">
            <span className="text-3xl font-bold text-blue-600">{formatBudget()}</span>
          </div>

          {/* Job Specifics */}
          <div className="space-y-3">
            <div className="flex items-center gap-3 text-gray-600">
              <Calendar className="h-5 w-5" />
              <span>{formatServiceDate()}</span>
            </div>

            <div className="flex items-center gap-3 text-gray-600">
              <Clock className="h-5 w-5" />
              <span>3 часа</span>
            </div>

            <div className="flex items-center gap-3 text-gray-600">
              <MapPin className="h-5 w-5" />
              <span>{jobQuery.data?.location}</span>
            </div>
          </div>

          {/* Show on Map Button */}
          <Button
            variant="outline"
            className="w-full border-blue-200 text-blue-600 hover:bg-blue-50"
            onClick={handleShowOnMap}
          >
            <Map className="h-4 w-4 mr-2" />
            показать на карте
          </Button>
        </CardContent>
      </Card>

      {/* Customer Information Card */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <Avatar className="h-12 w-12">
              <AvatarImage src={jobQuery.data?.employer?.user?.photo_url || undefined} />
              <AvatarFallback className="bg-gray-200 text-gray-600">
                {customerInitials}
              </AvatarFallback>
            </Avatar>

            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">
                {jobQuery.data?.employer?.user?.first_name} {jobQuery.data?.employer?.user?.last_name?.charAt(0)}.
              </h3>

              <div className="flex items-center gap-2 mt-1">
                <div className="flex items-center gap-1">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`h-4 w-4 ${i < Math.floor(customerRating)
                          ? "text-yellow-400 fill-current"
                          : i === Math.floor(customerRating) && customerRating % 1 !== 0
                            ? "text-yellow-400 fill-current opacity-50"
                            : "text-gray-300"
                        }`}
                    />
                  ))}
                </div>
                <span className="text-sm text-gray-600">
                  {customerRating} • {customerReviews} отзывов
                </span>
              </div>
            </div>
          </div>

          <Separator className="my-4" />

          {/* Customer Action Buttons - Only show for masters */}
          {isMaster && (
            <div className="flex gap-3">
              <Button
                variant="outline"
                className="flex-1 border-gray-300 text-gray-700 hover:bg-gray-50"
                onClick={handleCallCustomer}
              >
                <Phone className="h-4 w-4 mr-2" />
                Позвонить
              </Button>
              <Button
                variant="outline"
                className="flex-1 border-gray-300 text-gray-700 hover:bg-gray-50"
                onClick={handleMessageCustomer}
              >
                <MessageCircle className="h-4 w-4 mr-2" />
                Написать
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Attachments Section - Readonly for masters */}
      <Card>
        <CardContent className="p-6">
          <AttachmentsView
            attachments={attachmentsQuery.data || []}
            onUpload={handleUploadAttachments}
            onDelete={handleDeleteAttachment}
            onUploadSuccess={handleAttachmentUploadSuccess}
            onDeleteSuccess={handleAttachmentDeleteSuccess}
            isLoading={attachmentsQuery.isLoading}
            title="Вложения"
            description="Файлы, прикрепленные к заказу"
            readonly={isMaster} // Readonly for masters, editable for job owners
          />
        </CardContent>
      </Card>

      {/* Job Action Buttons - Only show for masters */}
      {isMaster && (
        <div className="space-y-3">
          <Button
            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            onClick={handleApplyToJob}
            disabled={applyJobMutation.isPending}
          >
            {applyJobMutation.isPending ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            ) : (
              <CheckCircle className="h-4 w-4 mr-2" />
            )}
            Подать заявку
          </Button>
        </div>
      )}
    </div>
  );
}
