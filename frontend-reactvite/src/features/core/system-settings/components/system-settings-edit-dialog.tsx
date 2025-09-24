import { FormDialog } from "@/components/dialogs/form-dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { useDialogControl } from "@/hooks/use-dialog-control";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useEffect } from "react";
import { z } from "zod";
import { toast } from "sonner";

const systemSettingsFormSchema = z.object({
  id: z.number(),
  key: z.string(),
  value: z.string().min(1, "Value is required"),
  description: z.string().max(500, "Description must be less than 500 characters"),
  setting_type: z.string(),
  is_active: z.boolean(),
});

export type SystemSettingsFormData = z.infer<typeof systemSettingsFormSchema>;

const loadSettingDetailQueryKey = 'system-setting-detail';

interface SystemSettingsEditDialogProps {
  control: ReturnType<typeof useDialogControl<SystemSettingsFormData>>;
  onSave?: (data: SystemSettingsFormData) => void;
  onCancel?: () => void;
}

export function SystemSettingsEditDialog({
  control,
  onSave,
  onCancel,
}: SystemSettingsEditDialogProps) {
  const queryClient = useQueryClient();
  const isEditMode = !!control.data?.id;

  const form = useForm<SystemSettingsFormData>({
    resolver: zodResolver(systemSettingsFormSchema),
    defaultValues: {
      id: 0,
      key: "",
      value: "",
      description: "",
      setting_type: "",
      is_active: true,
    },
  });

  // Load setting details for edit mode
  const loadSettingDetailQuery = useQuery({
    queryKey: [loadSettingDetailQueryKey, control.data?.id],
    queryFn: () => myApi.v1CoreSystemSettingsRetrieve({ id: control.data!.id! }).then(r => r.data),
    enabled: isEditMode && !!control.data?.id,
  });

  const updateMutation = useMutation({
    mutationFn: (data: SystemSettingsFormData) => 
      myApi.v1CoreSystemSettingsUpdate({ id: control.data!.id!, systemSettingsCreateUpdate: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['system-settings'] });
      queryClient.invalidateQueries({ queryKey: [loadSettingDetailQueryKey, control.data?.id] });
      toast.success("System setting updated successfully!");
      control.hide();
      onSave?.(form.getValues());
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update system setting");
    },
  });

  // Reset form when dialog opens or data changes
  useEffect(() => {
    if (control.isVisible && isEditMode) {
      const dataToUse = loadSettingDetailQuery.data || control.data;
      if (dataToUse) {
        form.reset({
          id: dataToUse.id,
          key: dataToUse.key,
          value: dataToUse.value,
          description: dataToUse.description || "",
          setting_type: dataToUse.setting_type,
          is_active: dataToUse.is_active ?? true,
        });
      }
    }
  }, [control.isVisible, isEditMode, loadSettingDetailQuery.data, control.data, form]);

  const onSubmit = (data: SystemSettingsFormData) => {
    updateMutation.mutate(data);
  };

  const handleCancel = () => {
    form.reset({
      id: 0,
      key: "",
      value: "",
      description: "",
      setting_type: "",
      is_active: true,
    });
    control.hide();
    onCancel?.();
  };

  const isLoading = updateMutation.isPending || loadSettingDetailQuery.isLoading;

  return (
    <FormDialog
      open={control.isVisible}
      onOpenChange={(open) => {
        if (!open) {
          form.reset({
            id: 0,
            key: "",
            value: "",
            description: "",
            setting_type: "",
            is_active: true,
          });
          control.hide();
        }
      }}
      title="Edit System Setting"
      description="Update the system setting value"
      onSubmit={form.handleSubmit(onSubmit)}
      onCancel={handleCancel}
      isLoading={isLoading}
      submitText="Update"
    >
      <Form {...form}>
        <div className="space-y-4">
          <FormField
            control={form.control}
            name="key"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Key</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    disabled
                    className="bg-gray-50"
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
                    {...field}
                    disabled
                    className="bg-gray-50 min-h-[80px]"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="setting_type"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Type</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    disabled
                    className="bg-gray-50"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="value"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Value *</FormLabel>
                <FormControl>
                  <Input
                    placeholder="Enter new value"
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
            name="is_active"
            render={({ field }) => (
              <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                <div className="space-y-0.5">
                  <FormLabel className="text-base">Active</FormLabel>
                  <div className="text-sm text-muted-foreground">
                    Whether this setting is active
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
