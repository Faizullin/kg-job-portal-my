import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { MultiCombobox } from "@/components/ui/combobox";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, MapPin, Save } from "lucide-react";
import React, { useMemo } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const clientProfileSchema = z.object({
  preferred_services: z.array(z.string()),
});

type ClientProfileFormData = z.infer<typeof clientProfileSchema>;

const loadClientProfileQueryKey = "client-profile";

export function ClientProfileForm() {
  const queryClient = useQueryClient();

  const loadClientProfileQuery = useQuery({
    queryKey: [loadClientProfileQueryKey],
    queryFn: async () => {
      const response = await myApi.v1UsersClientRetrieve();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  // Fetch service categories for preferred areas
  const loadServiceCategoriesQuery = useQuery({
    queryKey: ["service-subcategories"],
    queryFn: async () => {
      const response = await myApi.v1CoreServiceSubcategoriesList();
      return response.data.results;
    },
  });
  const serviceCategoryOptions = useMemo(() => {
    return loadServiceCategoriesQuery.data?.map((category) => ({
      label: `${category.name} [#${category.id}]`,
      value: category.id.toString(),
    })) || [];
  }, [loadServiceCategoriesQuery.data]);

  const form = useForm<ClientProfileFormData>({
    resolver: zodResolver(clientProfileSchema),
    defaultValues: {
      preferred_services:  [],
    },
  });

  React.useEffect(() => {
    const profileData = loadClientProfileQuery.data;
    if (profileData) {
      form.reset({
        preferred_services: (profileData.preferred_services || []).map(i => i.toString()),
      });
    }
  }, [loadClientProfileQuery.data, form]);

  const updateClientMutation = useMutation({
    mutationFn: async (data: ClientProfileFormData) => {
      const transformedData = {
        ...data,
        preferred_services: data.preferred_services.map(i => parseInt(i)) 
      }
      const response = await myApi.v1UsersClientPartialUpdate({ patchedClientUpdate: transformedData });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-profile"] });
      toast.success("Client profile updated successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Failed to update profile");
    },
  });

  const onSubmit = async (data: ClientProfileFormData) => {
    await updateClientMutation.mutateAsync(data);
  };

  if (loadClientProfileQuery.isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="ml-2">Loading profile...</span>
      </div>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Preferred Service Areas
          </h3>

          <FormField
            control={form.control}
            name="preferred_services"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Select Preferred Services</FormLabel>
                <FormControl>
                  <MultiCombobox
                    options={serviceCategoryOptions}
                    value={field.value}
                    onValueChange={field.onChange}
                    placeholder="Select service areas..."
                    searchPlaceholder="Search services..."
                    emptyText="No services found."
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {form.watch("preferred_services")?.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Selected services:</p>
              <div className="flex flex-wrap gap-2">
                {form.watch("preferred_services")?.map((areaId) => {
                  const category = serviceCategoryOptions?.find((cat) => cat.value === areaId);
                  return (
                    <Badge key={areaId} variant="secondary" className="flex items-center gap-1">
                      {category?.label}
                      <button
                        type="button"
                        onClick={() => {
                          const currentAreas = form.getValues("preferred_services") || [];
                          form.setValue("preferred_services", currentAreas.filter(id => id !== areaId));
                        }}
                        className="ml-1 hover:text-destructive"
                      >
                        ×
                      </button>
                    </Badge>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end">
          <Button type="submit" disabled={updateClientMutation.isPending}>
            {updateClientMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            {updateClientMutation.isPending ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </form>
    </Form>
  );
}
