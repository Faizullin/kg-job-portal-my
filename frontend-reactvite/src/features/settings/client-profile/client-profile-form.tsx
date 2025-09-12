import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { DollarSign, Loader2, MapPin, Save } from "lucide-react";
import React from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const clientProfileSchema = z.object({
  preferred_service_areas: z.array(z.string()).optional(),
  budget_preferences: z.object({
    min_budget: z.number().min(0).optional(),
    max_budget: z.number().min(0).optional(),
    currency: z.string().optional(),
  }).optional(),
});

type ClientProfileFormData = z.infer<typeof clientProfileSchema>;

export function ClientProfileForm() {
  const queryClient = useQueryClient();

  const { data: profileData, isLoading: isProfileLoading } = useQuery({
    queryKey: ["client-profile"],
    queryFn: async () => {
      const response = await myApi.v1UsersClientRetrieve();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  // Fetch service categories for preferred areas
  const { data: serviceCategories } = useQuery({
    queryKey: ["service-categories"],
    queryFn: async () => {
      const response = await myApi.v1CoreServiceCategoriesList();
      return response.data.results as any[];
    },
  });

  const form = useForm<ClientProfileFormData>({
    resolver: zodResolver(clientProfileSchema),
    defaultValues: {
      preferred_service_areas: profileData?.preferred_service_areas || [],
      budget_preferences: {
        min_budget: profileData?.budget_preferences?.min_budget || 0,
        max_budget: profileData?.budget_preferences?.max_budget || 1000,
        currency: profileData?.budget_preferences?.currency || "USD",
      },
    },
  });

  // Update form when profile data loads
  React.useEffect(() => {
    if (profileData) {
      form.reset({
        preferred_service_areas: profileData.preferred_service_areas || [],
        budget_preferences: {
          min_budget: profileData.budget_preferences?.min_budget || 0,
          max_budget: profileData.budget_preferences?.max_budget || 1000,
          currency: profileData.budget_preferences?.currency || "USD",
        },
      });
    }
  }, [profileData, form]);

  const updateClientMutation = useMutation({
    mutationFn: async (data: ClientProfileFormData) => {
      const response = await myApi.v1UsersClientPartialUpdate({ patchedClientUpdate: data });
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

  const addPreferredArea = (categoryId: string) => {
    const currentAreas = form.getValues("preferred_service_areas") || [];
    if (!currentAreas.includes(categoryId)) {
      form.setValue("preferred_service_areas", [...currentAreas, categoryId]);
    }
  };

  const removePreferredArea = (categoryId: string) => {
    const currentAreas = form.getValues("preferred_service_areas") || [];
    form.setValue("preferred_service_areas", currentAreas.filter(id => id !== categoryId));
  };

  if (isProfileLoading) {
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

          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {serviceCategories?.map((category: any) => (
                <Button
                  key={category.id}
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => addPreferredArea(category.id.toString())}
                  className="justify-start"
                >
                  {category.name}
                </Button>
              ))}
            </div>

            <div className="flex flex-wrap gap-2">
              {form.watch("preferred_service_areas")?.map((areaId) => {
                const category = serviceCategories?.find((cat: any) => cat.id.toString() === areaId);
                return (
                  <Badge key={areaId} variant="secondary" className="flex items-center gap-1">
                    {category?.name}
                    <button
                      type="button"
                      onClick={() => removePreferredArea(areaId)}
                      className="ml-1 hover:text-destructive"
                    >
                      ×
                    </button>
                  </Badge>
                );
              })}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Budget Preferences
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <FormField
              control={form.control}
              name="budget_preferences.min_budget"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Minimum Budget</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min="0"
                      placeholder="Enter minimum budget"
                      {...field}
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="budget_preferences.max_budget"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Maximum Budget</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min="0"
                      placeholder="Enter maximum budget"
                      {...field}
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 1000)}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="budget_preferences.currency"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Currency</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select currency" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="USD">USD ($)</SelectItem>
                      <SelectItem value="EUR">EUR (€)</SelectItem>
                      <SelectItem value="GBP">GBP (£)</SelectItem>
                      <SelectItem value="KGS">KGS (сом)</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
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
