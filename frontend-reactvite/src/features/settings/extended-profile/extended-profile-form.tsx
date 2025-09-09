import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { apiClient } from "@/lib/auth/backend-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, MapPin, Save } from "lucide-react";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const extendedProfileSchema = z.object({
  bio: z.string().max(1000, "Bio must be less than 1000 characters").optional(),
  date_of_birth: z.string().optional(),
  gender: z.enum(["male", "female", "other", "prefer_not_to_say", ""]).optional(),
  address: z.string().max(500, "Address must be less than 500 characters").optional(),
  city: z.string().max(100, "City must be less than 100 characters").optional(),
  state: z.string().max(100, "State must be less than 100 characters").optional(),
  country: z.string().max(100, "Country must be less than 100 characters").optional(),
  postal_code: z.string().max(20, "Postal code must be less than 20 characters").optional(),
  preferred_language: z.string().optional(),
});

type ExtendedProfileFormData = z.infer<typeof extendedProfileSchema>;

export function ExtendedProfileForm() {
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

  // Fetch available languages
  const { data: languages } = useQuery({
    queryKey: ["languages"],
    queryFn: async () => {
      const response = await apiClient.get("/core/languages/");
      return response.data;
    },
  });

  const form = useForm<ExtendedProfileFormData>({
    resolver: zodResolver(extendedProfileSchema),
    defaultValues: {
      bio: profileData?.bio || "",
      date_of_birth: profileData?.date_of_birth || "",
      gender: profileData?.gender || "",
      address: profileData?.address || "",
      city: profileData?.city || "",
      state: profileData?.state || "",
      country: profileData?.country || "",
      postal_code: profileData?.postal_code || "",
      preferred_language: profileData?.preferred_language || "",
    },
  });

  // Update form when profile data loads
  useEffect(() => {
    if (profileData) {
      form.reset({
        bio: profileData.bio || "",
        date_of_birth: profileData.date_of_birth || "",
        gender: profileData.gender || "",
        address: profileData.address || "",
        city: profileData.city || "",
        state: profileData.state || "",
        country: profileData.country || "",
        postal_code: profileData.postal_code || "",
        preferred_language: profileData.preferred_language || "",
      });
    }
  }, [profileData, form]);

  const updateProfileMutation = useMutation({
    mutationFn: async (data: ExtendedProfileFormData) => {
      const response = await apiClient.patch("/users/profile/", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-profile"] });
      toast.success("Profile updated successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Failed to update profile");
    },
  });

  const onSubmit = async (data: ExtendedProfileFormData) => {
    await updateProfileMutation.mutateAsync(data);
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
        <FormField
          control={form.control}
          name="bio"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Bio</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Tell us more about yourself..."
                  className="min-h-[100px]"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            control={form.control}
            name="date_of_birth"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Date of Birth</FormLabel>
                <FormControl>
                  <Input type="date" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="gender"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Gender</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select gender" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                    <SelectItem value="prefer_not_to_say">Prefer not to say</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Location Information
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormField
              control={form.control}
              name="address"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Address</FormLabel>
                  <FormControl>
                    <Textarea placeholder="Enter your address" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="city"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>City</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter your city" {...field} />
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
                  <FormLabel>State/Province</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter your state" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="country"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Country</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter your country" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="postal_code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Postal Code</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter postal code" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="preferred_language"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Preferred Language</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select language" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {languages?.map((language: any) => (
                        <SelectItem key={language.id} value={language.id.toString()}>
                          {language.name} ({language.native_name})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>

        <div className="flex justify-end">
          <Button type="submit" disabled={updateProfileMutation.isPending}>
            {updateProfileMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            {updateProfileMutation.isPending ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </form>
    </Form>
  );
}
