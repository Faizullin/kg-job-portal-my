import { AttachmentsView } from "@/components/attachments/attachments-view";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { useDialogControl } from "@/hooks/use-dialog-control";
import { JobAssignmentStatusEnum, type JobAssignment } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { ru } from "date-fns/locale";
import { Calendar, Star } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { FormDialog } from "./form-dialog";

const completionFormSchema = z.object({
  completion_notes: z.string().min(1, "Completion notes are required").max(500, "Notes must be less than 500 characters"),
  rating: z.number().min(1, "Rating is required").max(5, "Rating must be between 1 and 5"),
  review: z.string().optional(),
});

export type CompletionFormData = z.infer<typeof completionFormSchema>;

interface AssignmentCompletionDialogProps {
  control: ReturnType<typeof useDialogControl<JobAssignment>>;
  onComplete?: (assignment: JobAssignment) => void;
  onCancel?: () => void;
}

export function AssignmentCompletionDialog({
  control,
  onComplete,
  onCancel,
}: AssignmentCompletionDialogProps) {
  const queryClient = useQueryClient();
  const [selectedRating, setSelectedRating] = useState(0);
  const assignment = control.data;

  const completionForm = useForm<CompletionFormData>({
    resolver: zodResolver(completionFormSchema),
    defaultValues: {
      completion_notes: "",
      rating: 0,
      review: "",
    },
  });

  // Complete assignment mutation
  const completeAssignmentMutation = useMutation({
    mutationFn: async (data: CompletionFormData) => {
      if (!assignment) throw new Error("No assignment data");

      // Update assignment status to completed
      await myApi.v1AssignmentsPartialUpdate({
        id: assignment.id.toString(),
        patchedJobAssignmentRequest: {
          status: JobAssignmentStatusEnum.completed,
        }
      });

      // Create rating and review
      if (data.rating > 0) {
        await myApi.v1AssignmentsRateCreate({
          id: assignment.id.toString(),
          ratingRequest: {
            client_rating: data.rating,
            client_review: data.review || "",
          }
        });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assignment-detail"] });
      queryClient.invalidateQueries({ queryKey: ["assignments"] });
      control.hide();
      setSelectedRating(0);
      toast.success("Assignment completed successfully!");
      onComplete?.(assignment!);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to complete assignment");
    },
  });

  // Customer initials
  const customerInitials = useMemo(() => {
    if (!assignment?.job?.employer?.user) return "U";
    const user = assignment.job.employer.user;
    if (user.first_name && user.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    return (user.username || user.email.split("@")[0] || "U").substring(0, 2).toUpperCase();
  }, [assignment?.job?.employer?.user]);

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

  // Handle completion
  const handleCompleteAssignment = useCallback((data: CompletionFormData) => {
    completeAssignmentMutation.mutate(data);
  }, [completeAssignmentMutation]);


  const handleCancel = useCallback(() => {
    completionForm.reset();
    setSelectedRating(0);
    control.hide();
    onCancel?.();
  }, [completionForm, control, onCancel]);

  if (!assignment || !assignment.job) {
    return null;
  }

  const job = assignment.job;

  return (
    <FormDialog
      open={control.isVisible}
      onOpenChange={(open) => {
        if (!open) {
          handleCancel();
        }
      }}
      title="Завершение работы"
      description="Подтвердите выполнение работы и оцените клиента"
      onSubmit={completionForm.handleSubmit(handleCompleteAssignment)}
      onCancel={handleCancel}
      submitText="Завершить"
      cancelText="Отмена"
      isLoading={completeAssignmentMutation.isPending}
      maxWidth="4xl"
    >
      <Form {...completionForm}>
        <div className="space-y-6">
        {/* Job Details */}
        <Card>
          <CardContent className="pt-6">
            <h3 className="font-semibold text-lg">{job.title}</h3>
            <div className="flex items-center gap-2 mt-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">{formatServiceDate(job.service_date || "")}</span>
            </div>
            <div className="text-primary font-semibold mt-2">{job.budget_min} тг</div>
            <div className="flex items-center gap-2 mt-2">
              <Avatar className="h-6 w-6">
                <AvatarImage src={job.employer?.user?.photo_url || undefined} alt="Client" />
                <AvatarFallback className="text-xs">{customerInitials}</AvatarFallback>
              </Avatar>
              <span className="text-sm">{job.employer?.user?.first_name} {job.employer?.user?.last_name}</span>
            </div>
          </CardContent>
        </Card>

        {/* Work Confirmation */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Подтвердите выполнение работы</CardTitle>
          </CardHeader>
          <CardContent>
            <AttachmentsView
              attachments={[]}
              onUpload={async (files) => {
                if (!assignment) return { success: false, files: [] };
                
                try {
                  await myApi.v1AssignmentsAttachmentsCreate({
                    assignmentId: assignment.id.toString(),
                    files: files
                  });
                  
                  return { success: true, files };
                } catch (error) {
                  console.error("Failed to upload completion photos:", error);
                  toast.error("Failed to upload photos");
                  return { success: false, files: [] };
                }
              }}
              onDelete={async () => {
                // Completion photos are typically not deleted during completion
                return;
              }}
              onUploadSuccess={() => {
                // Refresh assignment attachments if needed
                queryClient.invalidateQueries({ queryKey: ["assignment-attachments", assignment.id] });
              }}
              onDeleteSuccess={() => {
                // Refresh assignment attachments if needed
                queryClient.invalidateQueries({ queryKey: ["assignment-attachments", assignment.id] });
              }}
              title="Фотографии завершения работы"
              description="Загрузите фотографии выполненной работы"
            />
          </CardContent>
        </Card>

        {/* Client Rating */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Оцените клиента</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((rating) => (
                <Button
                  key={rating}
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="p-0 h-8 w-8"
                  onClick={() => {
                    setSelectedRating(rating);
                    completionForm.setValue("rating", rating);
                  }}
                >
                  <Star
                    className={`h-5 w-5 ${rating <= selectedRating
                      ? "text-yellow-500 fill-current"
                      : "text-gray-300"
                      }`}
                  />
                </Button>
              ))}
            </div>

            <FormField
              control={completionForm.control}
              name="review"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Textarea
                      placeholder="Напишите отзыв..."
                      className="min-h-[80px]"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </CardContent>
        </Card>

        {/* Completion Notes */}
        <FormField
          control={completionForm.control}
          name="completion_notes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Заметки о выполненной работе *</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Опишите выполненную работу, использованные материалы, рекомендации..."
                  className="min-h-[100px]"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        </div>
      </Form>
    </FormDialog>
  );
}
