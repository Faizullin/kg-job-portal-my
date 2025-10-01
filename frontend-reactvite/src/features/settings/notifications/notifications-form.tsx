import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel
} from "@/components/ui/form";
import { Switch } from "@/components/ui/switch";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, Loader2, Mail, Save, Smartphone } from "lucide-react";
import React from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const notificationsFormSchema = z.object({
  email_notifications: z.boolean(),
  push_notifications: z.boolean(),
  sms_notifications: z.boolean(),
});

type NotificationsFormValues = z.infer<typeof notificationsFormSchema>;

export function NotificationsForm() {
  const queryClient = useQueryClient();

  // Fetch notification preferences
  const { data: notificationData, isLoading } = useQuery({
    queryKey: ["notification-preferences"],
    queryFn: async () => {
      try {
        // Get user's notification preferences (single record)
        const response = await myApi.v1ProfileNotificationSettingsRetrieve();
        return response.data;
      } catch (error) {
        console.error("Error fetching notification preferences:", error);
        return null;
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  const form = useForm<NotificationsFormValues>({
    resolver: zodResolver(notificationsFormSchema),
    defaultValues: {
      email_notifications: true,
      push_notifications: true,
      sms_notifications: false,
    },
  });

  // Update form when data loads
  React.useEffect(() => {
    if (notificationData) {
      form.reset({
        email_notifications: notificationData.email_notifications,
        push_notifications: notificationData.push_notifications,
        sms_notifications: notificationData.sms_notifications,
      });
    }
  }, [notificationData, form]);

  // Update notification preferences mutation
  const updateNotificationMutation = useMutation({
    mutationFn: async (data: NotificationsFormValues) => {
      // Update user's notification preferences (single record)
      const response = await myApi.v1ProfileNotificationSettingsPartialUpdate({
        patchedUserNotificationSettings: data
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notification-preferences"] });
      toast.success("Notification preferences updated successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Failed to update notification preferences");
    },
  });

  const onSubmit = async (data: NotificationsFormValues) => {
    await updateNotificationMutation.mutateAsync(data);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="ml-2">Loading notification preferences...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Notification Status */}
      <div className="flex items-center space-x-2">
        <Badge variant="outline" className="text-xs">
          Notification Status
        </Badge>
        <Badge variant="secondary" className="text-xs">
          {notificationData ? "Configured" : "Default"}
        </Badge>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* General Notification Channels */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                <span>Notification Channels</span>
              </CardTitle>
              <CardDescription>
                Choose how you want to receive notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="email_notifications"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base flex items-center space-x-2">
                        <Mail className="h-4 w-4" />
                        <span>Email Notifications</span>
                      </FormLabel>
                      <FormDescription>
                        Receive notifications via email
                      </FormDescription>
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
                name="push_notifications"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base flex items-center space-x-2">
                        <Smartphone className="h-4 w-4" />
                        <span>Push Notifications</span>
                      </FormLabel>
                      <FormDescription>
                        Receive push notifications on your device
                      </FormDescription>
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
                name="sms_notifications"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base flex items-center space-x-2">
                        <Smartphone className="h-4 w-4" />
                        <span>SMS Notifications</span>
                      </FormLabel>
                      <FormDescription>
                        Receive notifications via SMS
                      </FormDescription>
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
            </CardContent>
          </Card>

          <div className="flex justify-end">
            <Button type="submit" disabled={updateNotificationMutation.isPending}>
              {updateNotificationMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              {updateNotificationMutation.isPending ? "Saving..." : "Save Preferences"}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
