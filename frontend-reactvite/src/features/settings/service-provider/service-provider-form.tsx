import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { apiClient } from "@/lib/auth/backend-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Briefcase, Clock, Loader2, MapPin, Save } from "lucide-react";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const serviceProviderSchema = z.object({
  business_name: z.string().min(2, "Business name must be at least 2 characters").optional(),
  business_description: z.string().max(1000, "Description must be less than 1000 characters").optional(),
  business_license: z.string().optional(),
  years_of_experience: z.number().min(0, "Experience must be 0 or more").optional(),
  service_areas: z.array(z.string()).optional(),
  travel_radius: z.number().min(1, "Travel radius must be at least 1 km").optional(),
  is_available: z.boolean().optional(),
  availability_schedule: z.record(z.string(), z.any()).optional(),
});

type ServiceProviderFormData = z.infer<typeof serviceProviderSchema>;

export function ServiceProviderForm() {
  const queryClient = useQueryClient();
  
  const { data: profileData, isLoading: isProfileLoading } = useQuery({
    queryKey: ["user-profile"],
    queryFn: async () => {
      const response = await apiClient.get("/profile/");
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  // Fetch service categories for service areas
  const { data: serviceCategories } = useQuery({
    queryKey: ["service-categories"],
    queryFn: async () => {
      const response = await apiClient.get("/core/service-categories/");
      return response.data;
    },
  });

  const form = useForm<ServiceProviderFormData>({
    resolver: zodResolver(serviceProviderSchema),
    defaultValues: {
      business_name: profileData?.business_name || "",
      business_description: profileData?.business_description || "",
      business_license: profileData?.business_license || "",
      years_of_experience: profileData?.years_of_experience || 0,
      service_areas: profileData?.service_areas || [],
      travel_radius: profileData?.travel_radius || 50,
      is_available: profileData?.is_available ?? true,
      availability_schedule: profileData?.availability_schedule || {},
    },
  });

  // Update form when profile data loads
  useEffect(() => {
    if (profileData) {
      form.reset({
        business_name: profileData.business_name || "",
        business_description: profileData.business_description || "",
        business_license: profileData.business_license || "",
        years_of_experience: profileData.years_of_experience || 0,
        service_areas: profileData.service_areas || [],
        travel_radius: profileData.travel_radius || 50,
        is_available: profileData.is_available ?? true,
        availability_schedule: profileData.availability_schedule || {},
      });
    }
  }, [profileData, form]);

  const updateProviderMutation = useMutation({
    mutationFn: async (data: ServiceProviderFormData) => {
      const response = await apiClient.patch("/users/provider/", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-profile"] });
      toast.success("Service provider profile updated successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Failed to update profile");
    },
  });

  const onSubmit = async (data: ServiceProviderFormData) => {
    await updateProviderMutation.mutateAsync(data);
  };

  const addServiceArea = (categoryId: string) => {
    const currentAreas = form.getValues("service_areas") || [];
    if (!currentAreas.includes(categoryId)) {
      form.setValue("service_areas", [...currentAreas, categoryId]);
    }
  };

  const removeServiceArea = (categoryId: string) => {
    const currentAreas = form.getValues("service_areas") || [];
    form.setValue("service_areas", currentAreas.filter(id => id !== categoryId));
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
            <Briefcase className="h-5 w-5" />
            Business Information
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormField
              control={form.control}
              name="business_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Business Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter your business name" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="business_license"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Business License</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter license number" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="years_of_experience"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Years of Experience</FormLabel>
                  <FormControl>
                    <Input 
                      type="number" 
                      min="0" 
                      placeholder="Enter years of experience" 
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
              name="travel_radius"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Travel Radius (km)</FormLabel>
                  <FormControl>
                    <Input 
                      type="number" 
                      min="1" 
                      placeholder="Enter travel radius" 
                      {...field}
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 50)}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="business_description"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Business Description</FormLabel>
                <FormControl>
                  <Textarea 
                    placeholder="Describe your business and services..." 
                    className="min-h-[100px]"
                    {...field} 
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Service Areas
          </h3>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {serviceCategories?.map((category: any) => (
                <Button
                  key={category.id}
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => addServiceArea(category.id.toString())}
                  className="justify-start"
                >
                  {category.name}
                </Button>
              ))}
            </div>
            
            <div className="flex flex-wrap gap-2">
              {form.watch("service_areas")?.map((areaId) => {
                const category = serviceCategories?.find((cat: any) => cat.id.toString() === areaId);
                return (
                  <Badge key={areaId} variant="secondary" className="flex items-center gap-1">
                    {category?.name}
                    <button
                      type="button"
                      onClick={() => removeServiceArea(areaId)}
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
            <Clock className="h-5 w-5" />
            Availability
          </h3>
          
          <FormField
            control={form.control}
            name="is_available"
            render={({ field }) => (
              <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                <div className="space-y-0.5">
                  <FormLabel className="text-base">
                    Available for Work
                  </FormLabel>
                  <p className="text-sm text-muted-foreground">
                    Toggle your availability for new service requests
                  </p>
                </div>
                <FormControl>
                  <Switch
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                </FormControl>
              </FormItem>
            )}
          />
        </div>

        <div className="flex justify-end">
          <Button type="submit" disabled={updateProviderMutation.isPending}>  
            {updateProviderMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            {updateProviderMutation.isPending ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </form>
    </Form>
  );
}
