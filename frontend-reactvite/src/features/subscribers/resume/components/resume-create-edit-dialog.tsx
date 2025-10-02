import { FormDialog } from "@/components/dialogs/form-dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useDialogControl } from "@/hooks/use-dialog-control";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const resumeFormSchema = z.object({
  id: z.number().optional(),
  title: z.string().min(1, "Title is required").max(200, "Title must be less than 200 characters"),
  content: z.string().min(1, "Content is required").max(5000, "Content must be less than 5000 characters"),
  status: z.enum(['draft', 'published', 'archived']).default('draft'),
});

export type ResumeFormData = z.infer<typeof resumeFormSchema>;

const loadResumeDetailQueryKey = 'resume-detail';

interface ResumeCreateEditDialogProps {
  control: ReturnType<typeof useDialogControl<ResumeFormData>>;
  onSave?: (data: ResumeFormData) => void;
  onCancel?: () => void;
}

export function ResumeCreateEditDialog({
  control,
  onSave,
  onCancel,
}: ResumeCreateEditDialogProps) {
  const queryClient = useQueryClient();
  const isEditMode = !!control.data?.id;

  const form = useForm<ResumeFormData>({
    resolver: zodResolver(resumeFormSchema),
    defaultValues: {
      title: "",
      content: "",
      status: "draft",
    },
  });

  // Load resume details for edit mode
  const loadResumeDetailQuery = useQuery({
    queryKey: [loadResumeDetailQueryKey, control.data?.id],
    queryFn: () => myApi.v1ResumesRetrieve({ id: control.data!.id! }).then(r => r.data),
    enabled: isEditMode && !!control.data?.id,
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: ResumeFormData) => {
      return myApi.v1ResumesCreate({ masterResumeRequest: data });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      toast.success("Resume created successfully!");
      control.hide();
      onSave?.(form.getValues());
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to create resume");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: ResumeFormData) => {
      return myApi.v1ResumesPartialUpdate({ 
        id: control.data!.id!, 
        patchedMasterResumeRequest: data 
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      queryClient.invalidateQueries({ queryKey: [loadResumeDetailQueryKey, control.data?.id] });
      toast.success("Resume updated successfully!");
      control.hide();
      onSave?.(form.getValues());
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update resume");
    },
  });

  // Reset form when dialog opens or data changes
  useEffect(() => {
    if (control.isVisible) {
      if (isEditMode) {
        const dataToUse = loadResumeDetailQuery.data || control.data;
        if (dataToUse) {
          form.reset({
            id: dataToUse.id,
            title: dataToUse.title,
            content: dataToUse.content,
            status: dataToUse.status || 'draft',
          });
        }
      } else {
        // Create mode - always reset to empty values
        form.reset({
          title: "",
          content: "",
          status: "draft",
        });
      }
    }
  }, [control.isVisible, isEditMode, loadResumeDetailQuery.data, control.data, form]);

  // Additional effect to ensure form is reset when dialog opens in create mode
  useEffect(() => {
    if (control.isVisible && !isEditMode) {
      // Force reset form for create mode
      form.reset({
        title: "",
        content: "",
        status: "draft",
      });
    }
  }, [control.isVisible, isEditMode, form]);

  const onSubmit = (data: ResumeFormData) => {
    if (isEditMode) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const handleCancel = () => {
    form.reset({
      title: "",
      content: "",
      status: "draft",
    });
    control.hide();
    onCancel?.();
  };

  const isLoading = createMutation.isPending || updateMutation.isPending || loadResumeDetailQuery.isLoading;

  return (
    <FormDialog
      open={control.isVisible}
      onOpenChange={(open) => {
        if (!open) {
          form.reset({
            title: "",
            content: "",
            status: "draft",
          });
          control.hide();
        }
      }}
      title={isEditMode ? "Edit Resume" : "Create Resume"}
      description={isEditMode ? "Update the resume details" : "Add a new resume"}
      onSubmit={form.handleSubmit(onSubmit)}
      onCancel={handleCancel}
      isLoading={isLoading}
      submitText={isEditMode ? "Update" : "Create"}
    >
      <Form {...form}>
        <div className="space-y-4">
          <FormField
            control={form.control}
            name="title"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Title *</FormLabel>
                <FormControl>
                  <Input
                    placeholder="Enter resume title"
                    {...field}
                    disabled={isLoading}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="status"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Status</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value} disabled={isLoading}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="published">Published</SelectItem>
                    <SelectItem value="archived">Archived</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="content"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Content *</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder="Enter resume content..."
                    className="min-h-[200px]"
                    {...field}
                    disabled={isLoading}
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
