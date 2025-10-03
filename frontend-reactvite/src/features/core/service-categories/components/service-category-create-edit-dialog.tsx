import { FormDialog } from "@/components/dialogs/form-dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
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

const serviceCategoryFormSchema = z.object({
  id: z.number().optional(),
  name: z.string().min(1, "Name is required").max(100, "Name must be less than 100 characters"),
  description: z.string().max(500, "Description must be less than 500 characters"),
  is_active: z.boolean(),
  featured: z.boolean(),
});

export type ServiceCategoryFormData = z.infer<typeof serviceCategoryFormSchema>;

const loadCategoryDetailQueryKey = 'service-category-detail';

interface ServiceCategoryCreateEditDialogProps {
  control: ReturnType<typeof useDialogControl<ServiceCategoryFormData>>;
  onSave?: (data: ServiceCategoryFormData) => void;
  onCancel?: () => void;
}

export function ServiceCategoryCreateEditDialog({
  control,
  onSave,
  onCancel,
}: ServiceCategoryCreateEditDialogProps) {
  const queryClient = useQueryClient();
  const isEditMode = !!control.data?.id;

  const form = useForm<ServiceCategoryFormData>({
    resolver: zodResolver(serviceCategoryFormSchema),
    defaultValues: {
      name: "",
      description: "",
      is_active: true,
      featured: false,
    },
  });

  // Load category details for edit mode
  const loadCategoryDetailQuery = useQuery({
    queryKey: [loadCategoryDetailQueryKey, control.data?.id],
    queryFn: () => myApi.v1CoreServiceCategoriesRetrieve({ id: control.data!.id! }).then(r => r.data),
    enabled: isEditMode && !!control.data?.id,
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: ServiceCategoryFormData) =>
      myApi.v1CoreServiceCategoriesCreate({ serviceCategoryCreateUpdateRequest: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['service-categories'] });
      toast.success("Service category created successfully!");
      control.hide();
      onSave?.(form.getValues());
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to create service category");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: ServiceCategoryFormData) =>
      myApi.v1CoreServiceCategoriesUpdate({ id: control.data!.id!, serviceCategoryCreateUpdateRequest: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['service-categories'] });
      queryClient.invalidateQueries({ queryKey: [loadCategoryDetailQueryKey, control.data?.id] });
      toast.success("Service category updated successfully!");
      control.hide();
      onSave?.(form.getValues());
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update service category");
    },
  });

  // Reset form when dialog opens or data changes
  useEffect(() => {
    if (control.isVisible) {
      if (isEditMode) {
        const dataToUse = loadCategoryDetailQuery.data || control.data;
        if (dataToUse) {
          form.reset({
            id: dataToUse.id,
            name: dataToUse.name,
            description: dataToUse.description || "",
            is_active: dataToUse.is_active ?? true,
            featured: dataToUse.featured ?? false,
          });
        }
      } else {
        // Create mode - always reset to empty values
        form.reset({
          name: "",
          description: "",
          is_active: true,
          featured: false,
        });
      }
    }
  }, [control.isVisible, isEditMode, loadCategoryDetailQuery.data, control.data, form]);

  // Additional effect to ensure form is reset when dialog opens in create mode
  useEffect(() => {
    if (control.isVisible && !isEditMode) {
      // Force reset form for create mode
      form.reset({
        name: "",
        description: "",
        is_active: true,
        featured: false,
      });
    }
  }, [control.isVisible, isEditMode, form]);

  const onSubmit = (data: ServiceCategoryFormData) => {
    if (isEditMode) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const handleCancel = () => {
    form.reset({
      name: "",
      description: "",
      is_active: true,
      featured: false,
    });
    control.hide();
    onCancel?.();
  };

  const isLoading = createMutation.isPending || updateMutation.isPending || loadCategoryDetailQuery.isLoading;

  return (
    <FormDialog
      open={control.isVisible}
      onOpenChange={(open) => {
        if (!open) {
          form.reset({
            name: "",
            description: "",
            is_active: true,
            featured: false,
          });
          control.hide();
        }
      }}
      title={isEditMode ? "Edit Service Category" : "Create Service Category"}
      description={isEditMode ? "Update the service category details" : "Add a new service category"}
      onSubmit={form.handleSubmit(onSubmit)}
      onCancel={handleCancel}
      isLoading={isLoading}
      submitText={isEditMode ? "Update" : "Create"}
    >
      <Form {...form}>
        <div className="space-y-4">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Name *</FormLabel>
                <FormControl>
                  <Input
                    placeholder="Enter category name"
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
            name="description"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Description</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder="Enter category description"
                    className="min-h-[80px]"
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
              name="is_active"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Active</FormLabel>
                    <div className="text-sm text-muted-foreground">
                      Whether this category is active and visible
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
              name="featured"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Featured</FormLabel>
                    <div className="text-sm text-muted-foreground">
                      Whether this category is featured
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