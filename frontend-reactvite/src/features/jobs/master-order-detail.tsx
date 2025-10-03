import { AttachmentsView } from "@/components/attachments/attachments-view";
import { AssignmentCompletionDialog } from "@/components/dialogs/assignment-completion-dialog";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useDialogControl } from "@/hooks/use-dialog-control";
import { type InitChatRequestRequest, type JobAssignment } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useQuery } from "@tanstack/react-query";
import { useNavigate, useParams } from "@tanstack/react-router";
import { format } from "date-fns";
import { ru } from "date-fns/locale";
import {
  ArrowLeft,
  Calendar,
  Camera,
  CheckCircle,
  Clock,
  MapPin,
  MessageCircle,
  Phone,
  Settings,
  Star,
  User,
} from "lucide-react";
import { useCallback, useMemo } from "react";
import { toast } from "sonner";

const loadAssignmentDetailQueryKey = "assignment-detail";

export function MasterAssignmentDetail() {
  const { assignmentId } = useParams({ from: "/_authenticated/jobs/assginments/$assignmentId" });
  const navigate = useNavigate();
  const completionDialog = useDialogControl<JobAssignment>();

  // Load assignment details
  const assignmentQuery = useQuery({
    queryKey: [loadAssignmentDetailQueryKey, assignmentId],
    queryFn: () => myApi.v1AssignmentsRetrieve({ id: assignmentId! }).then(r => r.data),
    enabled: !!assignmentId,
  });

  // Load assignment attachments
  const attachmentsQuery = useQuery({
    queryKey: ["assignment-attachments", assignmentId],
    queryFn: () => myApi.v1AssignmentsAttachmentsList({ assignmentId: assignmentId! }).then(r => r.data),
    enabled: !!assignmentId && !!assignmentQuery.data,
  });


  const assignment = assignmentQuery.data;
  const job = assignment?.job;

  // Progress tracking steps
  const progressSteps = useMemo(() => [
    {
      id: "assigned",
      title: "Заказ принят",
      icon: CheckCircle,
      completed: assignment?.status === "assigned" || assignment?.status === "in_progress" || assignment?.status === "completed",
      current: assignment?.status === "assigned",
    },
    {
      id: "in_progress",
      title: "В процессе",
      icon: Settings,
      completed: assignment?.status === "completed",
      current: assignment?.status === "in_progress",
    },
    {
      id: "completed",
      title: "Завершено",
      icon: CheckCircle,
      completed: assignment?.status === "completed",
      current: assignment?.status === "completed",
    },
  ], [assignment?.status]);

  // Customer initials
  const customerInitials = useMemo(() => {
    if (!job?.employer?.user) return "U";
    const user = job.employer.user;
    if (user.first_name && user.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    return (user.username || user.email.split("@")[0] || "U").substring(0, 2).toUpperCase();
  }, [job?.employer?.user]);

  // Format service date
  const formatServiceDate = useCallback((dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return `Сегодня, ${format(date, "HH:mm", { locale: ru })}`;
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return `Завтра, ${format(date, "HH:mm", { locale: ru })}`;
    } else {
      return format(date, "dd MMM, HH:mm", { locale: ru });
    }
  }, []);

  // Handle completion dialog
  const handleCompleteAssignment = useCallback(() => {
    if (assignment) {
      completionDialog.show(assignment);
    }
  }, [assignment, completionDialog]);

  // Handle call customer
  const handleCallCustomer = useCallback(() => {
    toast.error("Phone number not available");
  }, []);

  // Handle message customer
  const handleMessageCustomer = useCallback(async () => {
    if (!job?.employer?.user?.id) return;

    try {
      const response = await myApi.v1ChatsRoomsInitChat({
        initChatRequestRequest: {
          user_id: job.employer.user.id,
          title: `Chat with ${job.employer.user.first_name} ${job.employer.user.last_name}`,
        } as InitChatRequestRequest
      });

      const chatRoom = response.data;
      if (chatRoom?.id) {
        navigate({
          to: "/chats",
          search: { chat_room_id: chatRoom.id }
        });
      }
    } catch (error) {
      console.error("Failed to create/find chat room:", error);
      toast.error("Failed to open chat");
    }
  }, [job?.employer?.user?.id, job?.employer?.user?.first_name, job?.employer?.user?.last_name, navigate]);

  if (assignmentQuery.isLoading) {
    return (
      <div className="container mx-auto p-4 space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-24 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (assignmentQuery.error || !assignment || !job) {
    return (
      <div className="container mx-auto p-4">
        <div className="text-center py-8">
          <h2 className="text-xl font-semibold text-red-600">Ошибка загрузки</h2>
          <p className="text-muted-foreground mt-2">Не удалось загрузить детали задания</p>
          <Button onClick={() => navigate({ to: "/app/master" })} className="mt-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Вернуться к заданиям
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate({ to: "/app/master" })}
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-2xl font-bold">Задание #{assignment.id}</h1>
      </div>

      {/* Job Details */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">{job.title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">{job.description}</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span>{formatServiceDate(job.service_date || "")}</span>
            </div>

            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span>3 часа</span>
            </div>

            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              <span>{job.location}</span>
            </div>
          </div>

          <div className="text-2xl font-bold text-primary">
            {job.budget_min} тг
          </div>

          <Button variant="outline" className="w-full">
            <MapPin className="h-4 w-4 mr-2" />
            Открыть на карте
          </Button>
        </CardContent>
      </Card>

      {/* Photos Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            Фотографии
          </CardTitle>
        </CardHeader>
        <CardContent>
          <AttachmentsView
            attachments={attachmentsQuery.data?.results || []}
            readonly={true}
            onUpload={async () => ({ success: true, files: [] })}
            onDelete={async () => { }}
          />
        </CardContent>
      </Card>

      {/* Client Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Клиент
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Avatar className="h-12 w-12">
              <AvatarImage src={job.employer?.user?.photo_url || undefined} alt="Client" />
              <AvatarFallback>{customerInitials}</AvatarFallback>
            </Avatar>

            <div className="flex-1">
              <h3 className="font-semibold">
                {job.employer?.user?.first_name} {job.employer?.user?.last_name}
              </h3>
              <div className="flex items-center gap-1">
                <Star className="h-4 w-4 text-yellow-500 fill-current" />
                <span className="text-sm text-muted-foreground">4.7</span>
              </div>
            </div>
          </div>

          <div className="flex gap-2 mt-4">
            <Button variant="outline" onClick={handleCallCustomer} className="flex-1">
              <Phone className="h-4 w-4 mr-2" />
              Позвонить
            </Button>
            <Button variant="outline" onClick={handleMessageCustomer} className="flex-1">
              <MessageCircle className="h-4 w-4 mr-2" />
              Написать
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Progress Tracking */}
      <Card>
        <CardHeader>
          <CardTitle>Статус заказа</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {progressSteps.map((step) => {
              const Icon = step.icon;
              return (
                <div key={step.id} className="flex items-center gap-3">
                  <div className={`flex items-center justify-center w-8 h-8 rounded-full ${step.completed
                    ? "bg-green-100 text-green-600"
                    : step.current
                      ? "bg-blue-100 text-blue-600"
                      : "bg-gray-100 text-gray-400"
                    }`}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <span className={`font-medium ${step.completed || step.current ? "text-foreground" : "text-muted-foreground"
                    }`}>
                    {step.title}
                  </span>
                  {step.current && (
                    <Badge variant="secondary" className="ml-auto">
                      Текущий
                    </Badge>
                  )}
                </div>
              );
            })}
          </div>

           {/* Complete Assignment Button */}
           {/* {assignment.status === "in_progress" && ( */}
             <Button
               onClick={handleCompleteAssignment}
               className="w-full"
               size="lg"
             >
               Завершить работу
             </Button>
           {/* )} */}
        </CardContent>
      </Card>


      {/* Completion Dialog */}
      <AssignmentCompletionDialog
        control={completionDialog}
        onComplete={() => {
          // Refresh the assignment data
          assignmentQuery.refetch();
        }}
      />
    </div>
  );
}
