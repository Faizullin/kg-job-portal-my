import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MultiCombobox } from "@/components/ui/combobox";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Briefcase, Clock, Loader2, MapPin, Save } from "lucide-react";
import { useEffect, useMemo } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const masterSchema = z.object({
  business_name: z.string().min(2, "Business name must be at least 2 characters").optional(),
  business_description: z.string().max(1000, "Description must be less than 1000 characters").optional(),
  service_areas: z.array(z.string()),
  services_offered: z.array(z.string()),
  works_remotely: z.boolean().optional(),
  accepts_clients_at_location: z.boolean().optional(),
  travels_to_clients: z.boolean().optional(),
  is_available: z.boolean().optional(),
});

type MasterFormData = z.infer<typeof masterSchema>;

const loadMasterQueryKey = "master-profile";

export function MasterForm() {
  const queryClient = useQueryClient();

  const loadMasterProfileQuery = useQuery({
    queryKey: [loadMasterQueryKey],
    queryFn: async () => {
      const response = await myApi.v1UsersMyMasterRetrieve();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  // Fetch service categories for services offered
  const { data: serviceCategories } = useQuery({
    queryKey: ["service-subcategories"],
    queryFn: async () => {
      const response = await myApi.v1CoreServiceSubcategoriesList();
      return response.data.results;
    },
  });

  // Fetch service areas for location-based services
  const { data: serviceAreas } = useQuery({
    queryKey: ["service-areas"],
    queryFn: async () => {
      const response = await myApi.v1CoreServiceAreasList();
      return response.data.results;
    },
  });

  const form = useForm<MasterFormData>({
    resolver: zodResolver(masterSchema),
    defaultValues: {
      business_name: "",
      business_description: "",
      service_areas: [],
      services_offered: [],
      works_remotely: false,
      accepts_clients_at_location: false,
      travels_to_clients: false,
      is_available: true,
    },
  });

  const watchedServicesOffered = form.watch("services_offered");
  const watchedServiceAreas = form.watch("service_areas");

  const serviceCategoryOptions = useMemo(() => {
    const allOptions = serviceCategories?.map((category) => ({
      label: `${category.name} [#${category.id}]`,
      value: category.id.toString(),
    })) || [];

    const userPreferences = watchedServicesOffered;
    const availableOptions = allOptions.filter(
      option => !userPreferences.includes(option.value)
    );
    const userPreferenceOptions = allOptions.filter(
      option => userPreferences.includes(option.value)
    );

    return {
      available: availableOptions,
      userPreferences: userPreferenceOptions,
      all: allOptions
    };
  }, [serviceCategories, watchedServicesOffered]);

  const serviceAreaOptions = useMemo(() => {
    const allOptions = serviceAreas?.map((area) => ({
      label: `${area.name} [#${area.id}]`,
      value: area.id.toString(),
    })) || [];

    const userPreferences = watchedServiceAreas;
    const availableOptions = allOptions.filter(
      option => !userPreferences.includes(option.value)
    );
    const userPreferenceOptions = allOptions.filter(
      option => userPreferences.includes(option.value)
    );

    return {
      available: availableOptions,
      userPreferences: userPreferenceOptions,
      all: allOptions
    };
  }, [serviceAreas, watchedServiceAreas]);

  useEffect(() => {
    const profileData = loadMasterProfileQuery.data;
    console.log(profileData);
    if (profileData) {
      form.reset({
        service_areas: (profileData.service_areas || []).map((id: number) => id.toString()),
        services_offered: (profileData.services_offered || []).map((id: number) => id.toString()),
        works_remotely: profileData.works_remotely || false,
        accepts_clients_at_location: profileData.accepts_clients_at_location || false,
        travels_to_clients: profileData.travels_to_clients || false,
        is_available: profileData.is_available || true,
      });
    }
  }, [loadMasterProfileQuery.data, form]);

  const updateProviderMutation = useMutation({
    mutationFn: async (data: MasterFormData) => {
      const transformedData = {
        ...data,
        service_areas: data.service_areas.map(id => parseInt(id)),
        services_offered: data.services_offered.map(id => parseInt(id))
      };
      const response = await myApi.v1UsersMyMasterPartialUpdate({ patchedMasterProfileCreateUpdate: transformedData });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadMasterQueryKey] });
      toast.success("Service provider profile updated successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Failed to update profile");
    },
  });

  const onSubmit = async (data: MasterFormData) => {
    await updateProviderMutation.mutateAsync(data);
  };

  if (loadMasterProfileQuery.isLoading) {
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
            <Briefcase className="h-5 w-5" />
            Services Offered
          </h3>

          <FormField
            control={form.control}
            name="services_offered"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Select Services You Offer</FormLabel>
                <FormControl>
                  <MultiCombobox
                    options={serviceCategoryOptions?.available || []}
                    value={field.value}
                    onValueChange={field.onChange}
                    placeholder="Select services..."
                    searchPlaceholder="Search services..."
                    emptyText="No services found."
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {form.watch("services_offered").length > 0 && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Selected services:</p>
              <div className="flex flex-wrap gap-2">
                {serviceCategoryOptions?.userPreferences?.map((service) => (
                  <Badge key={service.value} variant="secondary" className="flex items-center gap-1">
                    {service.label}
                    <button
                      type="button"
                      onClick={() => {
                        const currentServices = form.getValues("services_offered");
                        form.setValue("services_offered", currentServices.filter(id => id !== service.value));
                      }}
                      className="ml-1 hover:text-destructive"
                    >
                      ×
                    </button>
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Service Areas
          </h3>

          <FormField
            control={form.control}
            name="service_areas"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Select Service Areas</FormLabel>
                <FormControl>
                  <MultiCombobox
                    options={serviceAreaOptions?.available || []}
                    value={field.value}
                    onValueChange={field.onChange}
                    placeholder="Select service areas..."
                    searchPlaceholder="Search areas..."
                    emptyText="No areas found."
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {form.watch("service_areas").length > 0 && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Selected areas:</p>
              <div className="flex flex-wrap gap-2">
                {serviceAreaOptions?.userPreferences?.map((area) => (
                  <Badge key={area.value} variant="secondary" className="flex items-center gap-1">
                    {area.label}
                    <button
                      type="button"
                      onClick={() => {
                        const currentAreas = form.getValues("service_areas");
                        form.setValue("service_areas", currentAreas.filter(id => id !== area.value));
                      }}
                      className="ml-1 hover:text-destructive"
                    >
                      ×
                    </button>
                  </Badge>
                ))}
              </div>
            </div>
          )}
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

        <div className="space-y-4">
          <h3 className="text-lg font-medium flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Availability Options
          </h3>

          <div className="space-y-4">
            <FormField
              control={form.control}
              name="works_remotely"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">
                      Works Remotely
                    </FormLabel>
                    <div className="text-sm text-muted-foreground">
                      I can provide services remotely/online
                    </div>
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

            <FormField
              control={form.control}
              name="accepts_clients_at_location"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">
                      Accepts Clients at My Location
                    </FormLabel>
                    <div className="text-sm text-muted-foreground">
                      Clients can come to my business location
                    </div>
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

            <FormField
              control={form.control}
              name="travels_to_clients"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">
                      Travels to Clients
                    </FormLabel>
                    <div className="text-sm text-muted-foreground">
                      I can travel to client locations for services
                    </div>
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
