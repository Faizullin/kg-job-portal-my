import ComboBox2 from "@/components/combobox";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import type { Profession, ServiceArea, ServiceSubcategory } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import type { SelectOption } from "@/lib/types";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Briefcase, DollarSign, GraduationCap, Languages, Loader2, MapPin, Save, User } from "lucide-react";
import { useCallback, useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const masterSchema = z.object({
  profession: z.custom<Profession>().nullable().optional(),
  service_areas: z.array(z.custom<ServiceArea>()),
  services_offered: z.array(z.custom<ServiceSubcategory>()),
  about_description: z.string().optional(),
  current_location: z.string().optional(),
  hourly_rate: z.string().optional(),
  response_time_hours: z.number().optional(),
  work_experience_start_year: z.number().nullable().optional(),
  education_institution: z.string().optional(),
  education_years: z.string().optional(),
  languages: z.array(z.custom<SelectOption>()),
  works_remotely: z.boolean().optional(),
  accepts_clients_at_location: z.boolean().optional(),
  travels_to_clients: z.boolean().optional(),
  is_available: z.boolean().optional(),
});

type MasterFormData = z.infer<typeof masterSchema>;

const MASTER_PROFILE_QUERY_KEY = "master-profile";

// Predefined language options
const LANGUAGES: SelectOption[] = [
  { value: "english", label: "English" },
  { value: "spanish", label: "Spanish" },
  { value: "french", label: "French" },
  { value: "german", label: "German" },
  { value: "chinese", label: "Chinese" },
  { value: "arabic", label: "Arabic" },
  { value: "russian", label: "Russian" },
  { value: "portuguese", label: "Portuguese" },
  { value: "japanese", label: "Japanese" },
  { value: "korean", label: "Korean" },
  { value: "italian", label: "Italian" },
  { value: "turkish", label: "Turkish" },
];

export function MasterForm() {
  const queryClient = useQueryClient();

  const loadMasterProfileQuery = useQuery({
    queryKey: [MASTER_PROFILE_QUERY_KEY],
    queryFn: async () => {
      const response = await myApi.v1UsersMyMasterRetrieve();
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  const form = useForm<MasterFormData>({
    resolver: zodResolver(masterSchema),
    defaultValues: {
      profession: null,
      service_areas: [],
      services_offered: [],
      about_description: "",
      current_location: "",
      hourly_rate: "",
      response_time_hours: 24,
      work_experience_start_year: null,
      education_institution: "",
      education_years: "",
      languages: [],
      works_remotely: false,
      accepts_clients_at_location: false,
      travels_to_clients: false,
      is_available: true,
    },
  });

  const searchProfessions = useCallback(async (search: string, offset: number, limit: number) => {
    const response = await myApi.v1UsersProfessionsList({
      search,
      page: Math.floor(offset / limit) + 1,
      pageSize: limit,
    });
    return response.data.results || [];
  }, []);

  const searchServiceSubcategories = useCallback(async (search: string, offset: number, limit: number) => {
    const response = await myApi.v1CoreServiceSubcategoriesList({
      search,
      page: Math.floor(offset / limit) + 1,
      pageSize: limit,
    });
    return response.data.results || [];
  }, []);

  const searchServiceAreas = useCallback(async (search: string, offset: number, limit: number) => {
    const response = await myApi.v1CoreServiceAreasList({
      search,
      page: Math.floor(offset / limit) + 1,
      pageSize: limit,
    });
    return response.data.results || [];
  }, []);

  const searchLanguages = useCallback(async (search: string) => {
    const filtered = LANGUAGES.filter((lang) =>
      lang.label.toLowerCase().includes(search.toLowerCase())
    );
    return Promise.resolve(filtered);
  }, []);

  useEffect(() => {
    const profileData = loadMasterProfileQuery.data;
    if (profileData) {
      const loadRelatedData = async () => {
        const [professionData, areasData, servicesData] = await Promise.all([
          profileData.profession ? myApi.v1UsersProfessionsRetrieve({ id: profileData.profession }).then((r) => r.data).catch(() => null) : Promise.resolve(null),
          profileData.service_areas?.length ? myApi.v1CoreServiceAreasList({ idIn: profileData.service_areas }).then((r) => r.data.results).catch(() => []) : Promise.resolve([]),
          profileData.services_offered?.length ? myApi.v1CoreServiceSubcategoriesList({ idIn: profileData.services_offered }).then((r) => r.data.results).catch(() => []) : Promise.resolve([])
        ]);

        const languagesData = Array.isArray(profileData.languages)
          ? profileData.languages.map((langName: string) =>
            LANGUAGES.find(l => l.label.toLowerCase() === langName.toLowerCase()) ||
            LANGUAGES.find(l => l.value.toLowerCase() === langName.toLowerCase())
          ).filter((lang): lang is SelectOption => lang !== undefined)
          : [];

        form.reset({
          profession: professionData,
          service_areas: areasData || [],
          services_offered: servicesData || [],
          about_description: profileData.about_description || "",
          current_location: profileData.current_location || "",
          hourly_rate: profileData.hourly_rate || "",
          response_time_hours: profileData.response_time_hours || 24,
          work_experience_start_year: profileData.work_experience_start_year || null,
          education_institution: profileData.education_institution || "",
          education_years: profileData.education_years || "",
          languages: languagesData,
          works_remotely: profileData.works_remotely || false,
          accepts_clients_at_location: profileData.accepts_clients_at_location || false,
          travels_to_clients: profileData.travels_to_clients || false,
          is_available: profileData.is_available !== undefined ? profileData.is_available : true,
        });
      };

      loadRelatedData();
    }
  }, [loadMasterProfileQuery.data, form]);

  const updateProviderMutation = useMutation({
    mutationFn: async (data: MasterFormData) => {
      const transformedData = {
        profession: data.profession?.id || null,
        service_areas: data.service_areas.map(area => area.id),
        services_offered: data.services_offered.map(service => service.id),
        about_description: data.about_description,
        current_location: data.current_location,
        hourly_rate: data.hourly_rate || null,
        response_time_hours: data.response_time_hours,
        work_experience_start_year: data.work_experience_start_year,
        education_institution: data.education_institution,
        education_years: data.education_years,
        languages: data.languages.map(lang => lang.value),
        works_remotely: data.works_remotely,
        accepts_clients_at_location: data.accepts_clients_at_location,
        travels_to_clients: data.travels_to_clients,
        is_available: data.is_available,
      };
      const response = await myApi.v1UsersMyMasterPartialUpdate({
        patchedMasterProfileCreateUpdate: transformedData
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [MASTER_PROFILE_QUERY_KEY] });
      toast.success("Master profile updated successfully");
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
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        {/* Professional Information */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium flex items-center gap-2">
              <User className="h-5 w-5" />
              Professional Information
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              Your professional details and credentials
            </p>
          </div>
          <Separator />

          <FormField
            control={form.control}
            name="profession"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Profession</FormLabel>
                <FormControl>
                  <ComboBox2<Profession>
                    title="Select profession..."
                    value={field.value || undefined}
                    valueKey="id"
                    multiple={false}
                    renderLabel={(profession) => profession.name}
                    searchFn={searchProfessions}
                    onChange={field.onChange}
                  />
                </FormControl>
                <FormDescription>Your primary profession or occupation</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="about_description"
            render={({ field }) => (
              <FormItem>
                <FormLabel>About Me</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder="Tell clients about yourself, your experience, and what makes you unique..."
                    className="min-h-32"
                    {...field}
                  />
                </FormControl>
                <FormDescription>A brief description of your professional background</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="current_location"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Current Location</FormLabel>
                <FormControl>
                  <Input placeholder="e.g., New York, NY" {...field} />
                </FormControl>
                <FormDescription>Your city and country</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Services & Specialization */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium flex items-center gap-2">
              <Briefcase className="h-5 w-5" />
              Services & Specialization
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              Define the services you offer
            </p>
          </div>
          <Separator />

          <FormField
            control={form.control}
            name="services_offered"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Services Offered</FormLabel>
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
                <FormDescription>Select all services you can provide</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Service Areas & Availability */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              Service Areas & Availability
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              Where and how you provide your services
            </p>
          </div>
          <Separator />

          <FormField
            control={form.control}
            name="service_areas"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Service Areas</FormLabel>
                <FormControl>
                  <ComboBox2<ServiceArea>
                    title="Select service areas..."
                    value={field.value}
                    valueKey="id"
                    multiple
                    renderLabel={(area) => area.name}
                    searchFn={searchServiceAreas}
                    onChange={field.onChange}
                    badgeRenderType="outside"
                  />
                </FormControl>
                <FormDescription>Geographic areas where you provide services</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="works_remotely"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Works Remotely</FormLabel>
                    <FormDescription className="text-sm">
                      Provide services online
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
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
                    <FormLabel className="text-base">At My Location</FormLabel>
                    <FormDescription className="text-sm">
                      Clients come to me
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
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
                    <FormLabel className="text-base">Travel to Clients</FormLabel>
                    <FormDescription className="text-sm">
                      I travel to client location
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="is_available"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Available for Work</FormLabel>
                    <FormDescription className="text-sm">
                      Accept new requests
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  </FormControl>
                </FormItem>
              )}
            />
          </div>
        </div>

        {/* Pricing & Response Time */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Pricing & Response Time
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              Your rates and response time
            </p>
          </div>
          <Separator />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="hourly_rate"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Hourly Rate</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      placeholder="50.00"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>Your hourly rate in USD</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="response_time_hours"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Response Time (hours)</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      placeholder="24"
                      {...field}
                      onChange={(e) => field.onChange(Number(e.target.value))}
                    />
                  </FormControl>
                  <FormDescription>Typical response time in hours</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>

        {/* Experience & Education */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium flex items-center gap-2">
              <GraduationCap className="h-5 w-5" />
              Experience & Education
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              Your work experience and educational background
            </p>
          </div>
          <Separator />

          <FormField
            control={form.control}
            name="work_experience_start_year"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Work Experience Start Year</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="2015"
                    {...field}
                    onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : null)}
                    value={field.value || ""}
                  />
                </FormControl>
                <FormDescription>Year you started in this profession</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="education_institution"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Educational Institution</FormLabel>
                  <FormControl>
                    <Input placeholder="University of..." {...field} />
                  </FormControl>
                  <FormDescription>School or university name</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="education_years"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Education Years</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g., 2010-2014" {...field} />
                  </FormControl>
                  <FormDescription>Years attended</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>

        {/* Languages */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium flex items-center gap-2">
              <Languages className="h-5 w-5" />
              Languages
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              Languages you can communicate in
            </p>
          </div>
          <Separator />

          <FormField
            control={form.control}
            name="languages"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Languages Spoken</FormLabel>
                <FormControl>
                  <ComboBox2<SelectOption>
                    title="Select languages..."
                    value={field.value}
                    valueKey="value"
                    multiple
                    renderLabel={(lang) => lang.label}
                    searchFn={searchLanguages}
                    onChange={field.onChange}
                    badgeRenderType="inside"
                  />
                </FormControl>
                <FormDescription>Select all languages you can communicate in</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-6 border-t">
          <Button
            type="submit"
            disabled={updateProviderMutation.isPending}
            className="min-w-32"
          >
            {updateProviderMutation.isPending ? (
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
