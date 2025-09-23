import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Save } from "lucide-react";
import { useEffect, useMemo } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const profileSchema = z.object({
  username: z.string().min(2, "Username must be at least 2 characters"),
  email: z.email().optional(),
  description: z.string().max(500, "Description must be less than 500 characters").optional(),
  first_name: z.string().min(1, "First name is required").optional(),
  last_name: z.string().min(1, "Last name is required").optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

const loadUserProfileAdvancedQueryKey = "user-profile-advanced";

export function ProfileForm() {
  const queryClient = useQueryClient();

  const loadUserProfileAdvancedQuery = useQuery({
    queryKey: [loadUserProfileAdvancedQueryKey],
    queryFn: async () => {
      const response = await myApi.v1UsersProfileAdvancedRetrieve();
      return response.data.user_data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  const form = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      username: "",
      email: "",
      description: "",
      first_name:  "",
      last_name:  "",
    },
  });

  // Update form when profile data loads
  useEffect(() => {
    const profileData = loadUserProfileAdvancedQuery.data;
    if (profileData) {
      form.reset({
        username: profileData.username || "",
        email: profileData.email || "",
        description: profileData.description || "",
        first_name: profileData.first_name || "",
        last_name: profileData.last_name || "",
      });
    }
  }, [loadUserProfileAdvancedQuery.data, form]);

  const updateProfileMutation = useMutation({
    mutationFn: async (data: ProfileFormData) => {
      const response = await myApi.v1ProfilePartialUpdate({ patchedUserUpdate: data });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadUserProfileAdvancedQueryKey] });
      toast.success("Profile updated successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Failed to update profile");
    },
  });

  const uploadAvatar = async (file: File) => {
    const formData = new FormData();
    formData.append("photo", file);
    await myApi.axios.post("/api/v1/profile/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    await queryClient.invalidateQueries({ queryKey: [loadUserProfileAdvancedQueryKey] });
    toast.success("Profile image uploaded");
  };

  // const resetAvatar = async () => {
  //   await myApi.axios.delete("/api/v1/profile/");
  //   await queryClient.invalidateQueries({ queryKey: [loadUserProfileAdvancedQueryKey] });
  //   toast.success("Profile image reset");
  // };

  const onSubmit = async (data: ProfileFormData) => {
    await updateProfileMutation.mutateAsync(data);
  };

  const fullName = useMemo(() => {
    return `${loadUserProfileAdvancedQuery.data?.first_name || ""} ${loadUserProfileAdvancedQuery.data?.last_name || ""}`;
  }, [loadUserProfileAdvancedQuery.data]);

  if (loadUserProfileAdvancedQuery.isLoading) {
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
          <Card>
            <CardHeader>
              <CardTitle>Account Information</CardTitle>
              <CardDescription />
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-4">
                  <Avatar className="size-16">
                    <AvatarImage src={loadUserProfileAdvancedQuery.data?.photo_url ?? undefined} className="object-cover" />
                    <AvatarFallback>{(fullName || "").slice(0, 1)}</AvatarFallback>
                  </Avatar>
                  <div className="flex items-center gap-2">
                    <Input type="file" accept="image/*" onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) uploadAvatar(file);
                    }} />
                    {/* {loadUserProfileAdvancedQuery.data?.photo && (
                      <Button type="button" variant="outline" onClick={resetAvatar}>Reset</Button>
                    )} */}
                  </div>
                </div>
              </div>

              <Separator />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="first_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>First Name</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter first name" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="last_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Last Name</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter last name" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Display Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter display name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input type="email" placeholder="Enter email" {...field} />
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
                        placeholder="Tell us about yourself..."
                        className="min-h-[80px]"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

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
