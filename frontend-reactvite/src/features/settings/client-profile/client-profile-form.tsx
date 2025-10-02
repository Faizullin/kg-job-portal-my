import ComboBox2 from "@/components/combobox";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import type { PublicMasterProfile, ServiceSubcategory } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Briefcase, Heart, Loader2, Phone, Save } from "lucide-react";
import { useCallback, useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const clientProfileSchema = z.object({
  contact_phone: z.string().optional(),
  preferred_services: z.array(z.custom<ServiceSubcategory>()),
  favorite_masters: z.array(z.custom<PublicMasterProfile>()),
});

type ClientProfileFormData = z.infer<typeof clientProfileSchema>;

const CLIENT_PROFILE_QUERY_KEY = "client-profile";

export function ClientProfileForm() {
  const queryClient = useQueryClient();

  const loadClientProfileQuery = useQuery({
    queryKey: [CLIENT_PROFILE_QUERY_KEY],
    queryFn: async () => {
      const response = await myApi.v1UsersMyEmployerRetrieve();
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  const form = useForm<ClientProfileFormData>({
    resolver: zodResolver(clientProfileSchema),
    defaultValues: {
      contact_phone: "",
      preferred_services: [],
      favorite_masters: [],
    },
  });

  const searchServiceSubcategories = useCallback(async (search: string, offset: number, limit: number) => {
    const response = await myApi.v1CoreServiceSubcategoriesList({
      search,
      page: Math.floor(offset / limit) + 1,
      pageSize: limit,
    });
    return response.data.results || [];
  }, []);

  const searchMasters = useCallback(async (search: string, offset: number, limit: number) => {
    const response = await myApi.v1UsersMastersList({
      search,
      page: Math.floor(offset / limit) + 1,
      pageSize: limit,
    });
    return response.data.results || [];
  }, []);

  useEffect(() => {
    const profileData = loadClientProfileQuery.data;
    if (profileData) {
      const loadRelatedData = async () => {
        const [servicesData, mastersData] = await Promise.all([
          profileData.preferred_services?.length ? myApi.v1CoreServiceSubcategoriesList({ idIn: profileData.preferred_services }).then((r) => r.data.results).catch(() => []) : Promise.resolve([]),
          profileData.favorite_masters?.length ? myApi.v1UsersMastersList({ idIn: profileData.favorite_masters }).then((r) => r.data.results).catch(() => []) : Promise.resolve([])
        ]);

        form.reset({
          contact_phone: profileData.contact_phone || "",
          preferred_services: servicesData || [],
          favorite_masters: mastersData || [],
        });
      };

      loadRelatedData();
    }
  }, [loadClientProfileQuery.data, form]);

  const updateClientMutation = useMutation({
    mutationFn: async (data: ClientProfileFormData) => {
      const transformedData = {
        contact_phone: data.contact_phone,
        preferred_services: data.preferred_services.map(service => service.id),
        favorite_masters: data.favorite_masters.map(master => master.id),
      };
      const response = await myApi.v1UsersMyEmployerPartialUpdate({ 
        patchedEmployerProfileCreateUpdate: transformedData 
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CLIENT_PROFILE_QUERY_KEY] });
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
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        {/* Contact Information */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium flex items-center gap-2">
              <Phone className="h-5 w-5" />
              Contact Information
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              Your contact details for service providers
            </p>
          </div>
          <Separator />

          <FormField
            control={form.control}
            name="contact_phone"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Phone Number</FormLabel>
                <FormControl>
                  <Input
                    type="tel"
                    placeholder="Enter your phone number"
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Your contact phone number for service providers to reach you
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Preferred Services */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium flex items-center gap-2">
              <Briefcase className="h-5 w-5" />
              Preferred Services
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              Services you're interested in hiring for
            </p>
          </div>
          <Separator />

          <FormField
            control={form.control}
            name="preferred_services"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Select Preferred Services</FormLabel>
                <FormControl>
                  <ComboBox2<ServiceSubcategory>
                    title="Select services..."
                    value={field.value}
                    valueKey="id"
                    multiple
                    renderLabel={(service) => service.name}
                    searchFn={searchServiceSubcategories}
                    onChange={field.onChange}
                    badgeRenderType="outside"
                  />
                </FormControl>
                <FormDescription>Services you frequently need or are interested in</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Favorite Masters */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium flex items-center gap-2">
              <Heart className="h-5 w-5" />
              Favorite Service Providers
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              Your preferred service providers for quick access
            </p>
          </div>
          <Separator />

          <FormField
            control={form.control}
            name="favorite_masters"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Select Favorite Masters</FormLabel>
                <FormControl>
                  <ComboBox2<PublicMasterProfile>
                    title="Select masters..."
                    value={field.value}
                    valueKey="id"
                    multiple
                    renderLabel={(master) => master.user.username}
                    searchFn={searchMasters}
                    onChange={field.onChange}
                    badgeRenderType="outside"
                  />
                </FormControl>
                <FormDescription>Masters you've worked with and trust</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-6 border-t">
          <Button 
            type="submit" 
            disabled={updateClientMutation.isPending}
            className="min-w-32"
          >
            {updateClientMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </>
            )}
          </Button>
        </div>
      </form>
    </Form>
  );
}
