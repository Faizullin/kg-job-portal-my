import { FormDialog } from "@/components/dialogs/form-dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useDialogControl } from "@/hooks/use-dialog-control";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useEffect } from "react";
import { z } from "zod";
import { toast } from "sonner";

const serviceSubcategoryFormSchema = z.object({
  id: z.number().optional(),
  name: z.string().min(1, "Name is required").max(100, "Name must be less than 100 characters"),
  description: z.string().max(500, "Description must be less than 500 characters"),
  category: z.number().min(1, "Category is required"),
  is_active: z.boolean(),
  featured: z.boolean(),
  sort_order: z.number().min(1, "Sort order must be at least 1"),
});

export type ServiceSubcategoryFormData = z.infer<typeof serviceSubcategoryFormSchema>;

const loadSubcategoryDetailQueryKey = 'service-subcategory-detail';
const loadServiceCategoriesQueryKey = 'service-categories';

interface ServiceSubcategoryCreateEditDialogProps {
  control: ReturnType<typeof useDialogControl<ServiceSubcategoryFormData>>;
  onSave?: (data: ServiceSubcategoryFormData) => void;
  onCancel?: () => void;
}

export function ServiceSubcategoryCreateEditDialog({
  control,
  onSave,
  onCancel,
}: ServiceSubcategoryCreateEditDialogProps) {
  const queryClient = useQueryClient();
  const isEditMode = !!control.data?.id;

  const form = useForm<ServiceSubcategoryFormData>({
    resolver: zodResolver(serviceSubcategoryFormSchema),
    defaultValues: {
      name: "",
      description: "",
      category: 1,
      is_active: true,
      featured: false,
      sort_order: 1,
    },
  });

  // Load subcategory details for edit mode
  const loadSubcategoryDetailQuery = useQuery({
    queryKey: [loadSubcategoryDetailQueryKey, control.data?.id],
    queryFn: () => myApi.v1CoreServiceSubcategoriesRetrieve({ id: control.data!.id! }).then(r => r.data),
    enabled: isEditMode && !!control.data?.id,
  });

  // Load service categories for dropdown
  const loadServiceCategoriesQuery = useQuery({
    queryKey: [loadServiceCategoriesQueryKey],
    queryFn: () => myApi.v1CoreServiceCategoriesList({ pageSize: 100 }).then(r => r.data),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: ServiceSubcategoryFormData) => 
      myApi.v1CoreServiceSubcategoriesCreate({ serviceSubcategoryCreateUpdate: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['service-subcategories'] });
      toast.success("Service subcategory created successfully!");
      control.hide();
      onSave?.(form.getValues());
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to create service subcategory");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: ServiceSubcategoryFormData) => 
      myApi.v1CoreServiceSubcategoriesUpdate({ id: control.data!.id!, serviceSubcategoryCreateUpdate: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['service-subcategories'] });
      queryClient.invalidateQueries({ queryKey: [loadSubcategoryDetailQueryKey, control.data?.id] });
      toast.success("Service subcategory updated successfully!");
      control.hide();
      onSave?.(form.getValues());
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update service subcategory");
    },
  });

  // Reset form when dialog opens or data changes
  useEffect(() => {
    if (control.isVisible) {
      if (isEditMode) {
        const dataToUse = loadSubcategoryDetailQuery.data || control.data;
        if (dataToUse) {
          form.reset({
            id: dataToUse.id,
            name: dataToUse.name,
            description: dataToUse.description || "",
            category: dataToUse.category,
            is_active: dataToUse.is_active ?? true,
            featured: dataToUse.featured ?? false,
            sort_order: dataToUse.sort_order || 1,
          });
        }
      } else {
        // Create mode - always reset to empty values
        form.reset({
          name: "",
          description: "",
          category: 1,
          is_active: true,
          featured: false,
          sort_order: 1,
        });
      }
    }
  }, [control.isVisible, isEditMode, loadSubcategoryDetailQuery.data, control.data, form]);

  // Additional effect to ensure form is reset when dialog opens in create mode
  useEffect(() => {
    if (control.isVisible && !isEditMode) {
      // Force reset form for create mode
      form.reset({
        name: "",
        description: "",
        category: 1,
        is_active: true,
        featured: false,
        sort_order: 1,
      });
    }
  }, [control.isVisible, isEditMode, form]);

  const onSubmit = (data: ServiceSubcategoryFormData) => {
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
      category: 1,
      is_active: true,
      featured: false,
      sort_order: 1,
    });
    control.hide();
    onCancel?.();
  };

  const isLoading = createMutation.isPending || updateMutation.isPending || loadSubcategoryDetailQuery.isLoading;

  return (
    <FormDialog
      open={control.isVisible}
      onOpenChange={(open) => {
        if (!open) {
          form.reset({
            name: "",
            description: "",
            category: 1,
            is_active: true,
            featured: false,
            sort_order: 1,
          });
          control.hide();
        }
      }}
      title={isEditMode ? "Edit Service Subcategory" : "Create Service Subcategory"}
      description={isEditMode ? "Update the service subcategory details" : "Add a new service subcategory"}
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
                    placeholder="Enter subcategory name"
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
                    placeholder="Enter subcategory description"
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
              name="category"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Category *</FormLabel>
                  <Select
                    value={field.value?.toString()}
                    onValueChange={(value) => field.onChange(parseInt(value))}
                    disabled={isLoading}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {loadServiceCategoriesQuery.data?.results?.map((category) => (
                        <SelectItem key={category.id} value={category.id.toString()}>
                          {category.name}
                        </SelectItem>
                      ))}
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
                      Whether this subcategory is active
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
                      Whether this subcategory is featured
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
