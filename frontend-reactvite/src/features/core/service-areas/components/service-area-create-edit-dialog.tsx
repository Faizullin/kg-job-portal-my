import { FormDialog } from "@/components/dialogs/form-dialog";
import { MultiCombobox } from "@/components/ui/combobox";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { useDialogControl } from "@/hooks/use-dialog-control";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const serviceAreaFormSchema = z.object({
  id: z.number().optional(),
  name: z.string().min(1, "Name is required").max(100, "Name must be less than 100 characters"),
  city: z.string().min(1, "City is required").max(100, "City must be less than 100 characters"),
  state: z.string().min(1, "State is required").max(100, "State must be less than 100 characters"),
  country: z.string().min(1, "Country is required").max(100, "Country must be less than 100 characters"),
  is_active: z.boolean(),
  service_categories: z.array(z.string()),
});

export type ServiceAreaFormData = z.infer<typeof serviceAreaFormSchema>;

const loadAreaDetailQueryKey = 'service-area-detail';
const loadServiceCategoriesQueryKey = 'service-categories';

interface ServiceAreaCreateEditDialogProps {
  control: ReturnType<typeof useDialogControl<ServiceAreaFormData>>;
  onSave?: (data: ServiceAreaFormData) => void;
  onCancel?: () => void;
}

export function ServiceAreaCreateEditDialog({
  control,
  onSave,
  onCancel,
}: ServiceAreaCreateEditDialogProps) {
  const queryClient = useQueryClient();
  const isEditMode = !!control.data?.id;

  const form = useForm<ServiceAreaFormData>({
    resolver: zodResolver(serviceAreaFormSchema),
    defaultValues: {
      name: "",
      city: "",
      state: "",
      country: "",
      is_active: true,
      service_categories: [],
    },
  });

  // Load area details for edit mode
  const loadAreaDetailQuery = useQuery({
    queryKey: [loadAreaDetailQueryKey, control.data?.id],
    queryFn: () => myApi.v1CoreServiceAreasRetrieve({ id: control.data!.id! }).then(r => r.data),
    enabled: isEditMode && !!control.data?.id,
  });

  // Load service categories for combobox
  const loadServiceCategoriesQuery = useQuery({
    queryKey: [loadServiceCategoriesQueryKey],
    queryFn: () => myApi.v1CoreServiceCategoriesList({ pageSize: 100 }).then(r => r.data),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: ServiceAreaFormData) => {
      const transformedData = {
        ...data,
        service_categories: data.service_categories.map(id => parseInt(id)),
      };
      return myApi.v1CoreServiceAreasCreate({ serviceAreaCreateUpdateRequest: transformedData });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['service-areas'] });
      toast.success("Service area created successfully!");
      control.hide();
      onSave?.(form.getValues());
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to create service area");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: ServiceAreaFormData) => {
      const transformedData = {
        ...data,
        service_categories: data.service_categories.map(id => parseInt(id)),
      };
      return myApi.v1CoreServiceAreasUpdate({ id: control.data!.id!, serviceAreaCreateUpdateRequest: transformedData });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['service-areas'] });
      queryClient.invalidateQueries({ queryKey: [loadAreaDetailQueryKey, control.data?.id] });
      toast.success("Service area updated successfully!");
      control.hide();
      onSave?.(form.getValues());
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update service area");
    },
  });

  // Service category options for combobox
  const serviceCategoryOptions = useMemo(() => {
    if (!loadServiceCategoriesQuery.data?.results) return [];
    return loadServiceCategoriesQuery.data.results.map(category => ({
      value: category.id.toString(),
      label: category.name,
    }));
  }, [loadServiceCategoriesQuery.data]);

  // Reset form when dialog opens or data changes
  useEffect(() => {
    if (control.isVisible) {
      if (isEditMode) {
        const dataToUse = loadAreaDetailQuery.data || control.data;
        if (dataToUse) {
          form.reset({
            id: dataToUse.id,
            name: dataToUse.name,
            city: dataToUse.city,
            state: dataToUse.state,
            country: dataToUse.country,
            is_active: dataToUse.is_active ?? true,
            service_categories: dataToUse.service_categories.map(category => category.toString()) || [],
          });
        }
      } else {
        // Create mode - always reset to empty values
        form.reset({
          name: "",
          city: "",
          state: "",
          country: "",
          is_active: true,
          service_categories: [],
        });
      }
    }
  }, [control.isVisible, isEditMode, loadAreaDetailQuery.data, control.data, form]);

  // Additional effect to ensure form is reset when dialog opens in create mode
  useEffect(() => {
    if (control.isVisible && !isEditMode) {
      // Force reset form for create mode
      form.reset({
        name: "",
        city: "",
        state: "",
        country: "",
        is_active: true,
        service_categories: [],
      });
    }
  }, [control.isVisible, isEditMode, form]);

  const onSubmit = (data: ServiceAreaFormData) => {
    if (isEditMode) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const handleCancel = () => {
    form.reset({
      name: "",
      city: "",
      state: "",
      country: "",
      is_active: true,
      service_categories: [],
    });
    control.hide();
    onCancel?.();
  };

  const isLoading = createMutation.isPending || updateMutation.isPending || loadAreaDetailQuery.isLoading;

  return (
    <FormDialog
      open={control.isVisible}
      onOpenChange={(open) => {
        if (!open) {
          form.reset({
            name: "",
            city: "",
            state: "",
            country: "",
            is_active: true,
            service_categories: [],
          });
          control.hide();
        }
      }}
      title={isEditMode ? "Edit Service Area" : "Create Service Area"}
      description={isEditMode ? "Update the service area details" : "Add a new service area"}
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
                    placeholder="Enter area name"
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
              name="city"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>City *</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Enter city"
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
              name="state"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>State *</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Enter state"
                      {...field}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="country"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Country *</FormLabel>
                <FormControl>
                  <Input
                    placeholder="Enter country"
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
            name="service_categories"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Service Categories</FormLabel>
                <FormControl>
                  <MultiCombobox
                    options={serviceCategoryOptions}
                    value={field.value}
                    onValueChange={field.onChange}
                    placeholder="Select service categories..."
                    searchPlaceholder="Search categories..."
                    emptyText="No categories found"
                    disabled={isLoading}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="is_active"
            render={({ field }) => (
              <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                <div className="space-y-0.5">
                  <FormLabel className="text-base">Active</FormLabel>
                  <div className="text-sm text-muted-foreground">
                    Whether this area is active and available
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
      </Form>
    </FormDialog>
  );
}
