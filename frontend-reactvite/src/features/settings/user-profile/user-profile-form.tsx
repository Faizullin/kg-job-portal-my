import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Save } from "lucide-react";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const userProfileSchema = z.object({
  bio: z.string().max(1000).optional(),
  phone_number: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  country: z.string().optional(),
  postal_code: z.string().optional(),
});

type UserProfileFormData = z.infer<typeof userProfileSchema>;

export function UserProfileForm() {
  const queryClient = useQueryClient();

  const { data: profileData, isLoading } = useQuery({
    queryKey: ["job-portal-user-profile"],
    queryFn: async () => {
      const response = await myApi.v1UsersMyProfileAdvancedRetrieve();
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  const form = useForm<UserProfileFormData>({
    resolver: zodResolver(userProfileSchema),
    defaultValues: {
      bio: "",
      phone_number: "",
      address: "",
      city: "",
      state: "",
      country: "",
      postal_code: "",
    },
  });

  useEffect(() => {
    if (profileData) {
      form.reset({
        bio: profileData.bio || "",
        phone_number: profileData.phone_number || "",
        address: profileData.address || "",
        city: profileData.city || "",
        state: profileData.state || "",
        country: profileData.country || "",
        postal_code: profileData.postal_code || "",
      });
    }
  }, [profileData, form]);

  const updateProfileMutation = useMutation({
    mutationFn: async (data: UserProfileFormData) => {
      const response = await myApi.v1UsersMyProfileAdvancedPartialUpdate({
        patchedAdvancedUserProfileRetrieveUpdate: data,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["job-portal-user-profile"] });
      toast.success("User profile updated successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Failed to update user profile");
    },
  });

  const onSubmit = async (data: UserProfileFormData) => {
    await updateProfileMutation.mutateAsync(data);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="ml-2">Loading user profile...</span>
      </div>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>User Profile</CardTitle>
            <CardDescription>Extended profile details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <FormField
              control={form.control}
              name="bio"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Bio</FormLabel>
                  <FormControl>
                    <Textarea placeholder="Tell us about yourself" className="min-h-[100px]" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="phone_number"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Phone Number</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter phone" {...field} />
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
            </div>

            <FormField
              control={form.control}
              name="address"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Address</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter address" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FormField
                control={form.control}
                name="city"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>City</FormLabel>
                    <FormControl>
                      <Input placeholder="City" {...field} />
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
                      <Input placeholder="State/Province" {...field} />
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
                      <Input placeholder="Country" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
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
          </CardContent>
        </Card>
      </form>
    </Form>
  );
}


