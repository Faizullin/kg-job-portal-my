import { FormDialog } from "@/components/dialogs/form-dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { useDialogControl } from "@/hooks/use-dialog-control";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const supportFAQFormSchema = z.object({
  id: z.number().optional(),
  question: z.string().min(1, "Question is required").max(200, "Question must be less than 200 characters"),
  answer: z.string().min(1, "Answer is required").max(2000, "Answer must be less than 2000 characters"),
  category: z.enum(['account', 'general', 'reviews', 'safety', 'search', 'specialist']),
  is_active: z.boolean(),
  is_popular: z.boolean(),
  sort_order: z.number().min(1, "Sort order must be at least 1"),
});

export type SupportFAQFormData = z.infer<typeof supportFAQFormSchema>;

const loadFAQDetailQueryKey = 'support-faq-detail';

interface SupportFAQCreateEditDialogProps {
  control: ReturnType<typeof useDialogControl<SupportFAQFormData>>;
  onSave?: (data: SupportFAQFormData) => void;
  onCancel?: () => void;
}

export function SupportFAQCreateEditDialog({
  control,
  onSave,
  onCancel,
}: SupportFAQCreateEditDialogProps) {
  const queryClient = useQueryClient();
  const isEditMode = !!control.data?.id;

  const form = useForm<SupportFAQFormData>({
    resolver: zodResolver(supportFAQFormSchema),
    defaultValues: {
      question: "",
      answer: "",
      category: "general",
      is_active: true,
      is_popular: false,
      sort_order: 1,
    },
  });

  // Load FAQ details for edit mode
  const loadFAQDetailQuery = useQuery({
    queryKey: [loadFAQDetailQueryKey, control.data?.id],
    queryFn: () => myApi.v1CoreSupportFaqRetrieve({ id: control.data!.id! }).then(r => r.data),
    enabled: isEditMode && !!control.data?.id,
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: SupportFAQFormData) =>
      myApi.v1CoreSupportFaqCreate({ supportFAQCreateUpdateRequest: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['support-faq'] });
      toast.success("Support FAQ created successfully!");
      control.hide();
      onSave?.(form.getValues());
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to create support FAQ");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: SupportFAQFormData) =>
      myApi.v1CoreSupportFaqUpdate({ id: control.data!.id!, supportFAQCreateUpdateRequest: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['support-faq'] });
      queryClient.invalidateQueries({ queryKey: [loadFAQDetailQueryKey, control.data?.id] });
      toast.success("Support FAQ updated successfully!");
      control.hide();
      onSave?.(form.getValues());
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update support FAQ");
    },
  });

  // Reset form when dialog opens or data changes
  useEffect(() => {
    if (control.isVisible) {
      if (isEditMode) {
        const dataToUse = loadFAQDetailQuery.data || control.data;
        if (dataToUse) {
          form.reset({
            id: dataToUse.id,
            question: dataToUse.question,
            answer: dataToUse.answer,
            category: dataToUse.category,
            is_active: dataToUse.is_active ?? true,
            is_popular: dataToUse.is_popular ?? false,
            sort_order: dataToUse.sort_order || 1,
          });
        }
      } else {
        // Create mode - always reset to empty values
        form.reset({
          question: "",
          answer: "",
          category: "general",
          is_active: true,
          is_popular: false,
          sort_order: 1,
        });
      }
    }
  }, [control.isVisible, isEditMode, loadFAQDetailQuery.data, control.data, form]);

  // Additional effect to ensure form is reset when dialog opens in create mode
  useEffect(() => {
    if (control.isVisible && !isEditMode) {
      // Force reset form for create mode
      form.reset({
        question: "",
        answer: "",
        category: "general",
        is_active: true,
        is_popular: false,
        sort_order: 1,
      });
    }
  }, [control.isVisible, isEditMode, form]);

  const onSubmit = (data: SupportFAQFormData) => {
    if (isEditMode) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const handleCancel = () => {
    form.reset({
      question: "",
      answer: "",
      category: "general",
      is_active: true,
      is_popular: false,
      sort_order: 1,
    });
    control.hide();
    onCancel?.();
  };

  const isLoading = createMutation.isPending || updateMutation.isPending || loadFAQDetailQuery.isLoading;

  return (
    <FormDialog
      open={control.isVisible}
      onOpenChange={(open) => {
        if (!open) {
          form.reset({
            question: "",
            answer: "",
            category: "general",
            is_active: true,
            is_popular: false,
            sort_order: 1,
          });
          control.hide();
        }
      }}
      title={isEditMode ? "Edit Support FAQ" : "Create Support FAQ"}
      description={isEditMode ? "Update the support FAQ details" : "Add a new support FAQ"}
      onSubmit={form.handleSubmit(onSubmit)}
      onCancel={handleCancel}
      isLoading={isLoading}
      submitText={isEditMode ? "Update" : "Create"}
    >
      <Form {...form}>
        <div className="space-y-4">
          <FormField
            control={form.control}
            name="question"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Question *</FormLabel>
                <FormControl>
                  <Input
                    placeholder="What is your question?"
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
            name="answer"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Answer *</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder="Provide a detailed answer..."
                    className="min-h-[120px]"
                    {...field}
                    disabled={isLoading}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="category"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Category *</FormLabel>
                  <Select
                    value={field.value}
                    onValueChange={field.onChange}
                    disabled={isLoading}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="account">Account</SelectItem>
                      <SelectItem value="general">General</SelectItem>
                      <SelectItem value="reviews">Reviews</SelectItem>
                      <SelectItem value="safety">Safety</SelectItem>
                      <SelectItem value="search">Search</SelectItem>
                      <SelectItem value="specialist">Specialist</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="sort_order"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Sort Order *</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      placeholder="1"
                      {...field}
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 1)}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="is_active"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Active</FormLabel>
                    <div className="text-sm text-muted-foreground">
                      Whether this FAQ is active
                    </div>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                      disabled={isLoading}
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="is_popular"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Popular</FormLabel>
                    <div className="text-sm text-muted-foreground">
                      Whether this FAQ is popular
                    </div>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                      disabled={isLoading}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
          </div>
        </div>
      </Form>
    </FormDialog>
  );
}
