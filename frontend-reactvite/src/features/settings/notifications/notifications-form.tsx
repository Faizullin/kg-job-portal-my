import React from "react";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Loader2, Save, Bell, Mail, Smartphone, Clock } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import myApi from "@/lib/api/my-api";

const notificationsFormSchema = z.object({
  // General notification preferences
  email_notifications: z.boolean(),
  push_notifications: z.boolean(),
  sms_notifications: z.boolean(),
  in_app_notifications: z.boolean(),
  
  // Specific notification types
  order_updates: z.boolean(),
  bid_notifications: z.boolean(),
  payment_notifications: z.boolean(),
  chat_notifications: z.boolean(),
  promotional_notifications: z.boolean(),
  system_notifications: z.boolean(),
  
  // Timing preferences
  quiet_hours_start: z.string().optional(),
  quiet_hours_end: z.string().optional(),
  timezone: z.string(),
  
  // Frequency
  digest_frequency: z.enum(['immediate', 'hourly', 'daily', 'weekly']),
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
        const response = await myApi.v1NotificationsSettingsRetrieve();
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
      in_app_notifications: true,
      order_updates: true,
      bid_notifications: true,
      payment_notifications: true,
      chat_notifications: true,
      promotional_notifications: false,
      system_notifications: true,
      timezone: 'UTC',
      digest_frequency: 'immediate',
    },
  });

  // Update form when data loads
  React.useEffect(() => {
    if (notificationData) {
      form.reset({
        email_notifications: notificationData.email_notifications ?? true,
        push_notifications: notificationData.push_notifications ?? true,
        sms_notifications: notificationData.sms_notifications ?? false,
        in_app_notifications: notificationData.in_app_notifications ?? true,
        order_updates: notificationData.order_updates ?? true,
        bid_notifications: notificationData.bid_notifications ?? true,
        payment_notifications: notificationData.payment_notifications ?? true,
        chat_notifications: notificationData.chat_notifications ?? true,
        promotional_notifications: notificationData.promotional_notifications ?? false,
        system_notifications: notificationData.system_notifications ?? true,
        quiet_hours_start: notificationData.quiet_hours_start || '',
        quiet_hours_end: notificationData.quiet_hours_end || '',
        timezone: notificationData.timezone || 'UTC',
        digest_frequency: notificationData.digest_frequency || 'immediate',
      });
    }
  }, [notificationData, form]);

  // Update notification preferences mutation
  const updateNotificationMutation = useMutation({
    mutationFn: async (data: NotificationsFormValues) => {
      // Update user's notification preferences (single record)
      const response = await myApi.v1NotificationsSettingsPartialUpdate({
        patchedNotificationSettingUpdate: data
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

              <FormField
                control={form.control}
                name="in_app_notifications"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base flex items-center space-x-2">
                        <Bell className="h-4 w-4" />
                        <span>In-App Notifications</span>
                      </FormLabel>
                      <FormDescription>
                        Show notifications within the application
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

          {/* Specific Notification Types */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                <span>Notification Types</span>
              </CardTitle>
              <CardDescription>
                Choose which types of notifications you want to receive
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="order_updates"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">Order Updates</FormLabel>
                      <FormDescription>
                        Notifications about order status changes
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
                name="bid_notifications"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">Bid Notifications</FormLabel>
                      <FormDescription>
                        Notifications about new bids and bid updates
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
                name="payment_notifications"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">Payment Notifications</FormLabel>
                      <FormDescription>
                        Notifications about payment status and transactions
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
                name="chat_notifications"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">Chat Notifications</FormLabel>
                      <FormDescription>
                        Notifications about new messages and chat activity
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
                name="promotional_notifications"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">Promotional Notifications</FormLabel>
                      <FormDescription>
                        Marketing and promotional content
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
                name="system_notifications"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">System Notifications</FormLabel>
                      <FormDescription>
                        Important system updates and announcements
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                        disabled
                        aria-readonly
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Timing and Frequency */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Clock className="h-5 w-5" />
                <span>Timing & Frequency</span>
              </CardTitle>
              <CardDescription>
                Configure when and how often you receive notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="digest_frequency"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Digest Frequency</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select frequency" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="immediate">Immediate</SelectItem>
                        <SelectItem value="hourly">Hourly</SelectItem>
                        <SelectItem value="daily">Daily</SelectItem>
                        <SelectItem value="weekly">Weekly</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      How often to receive notification digests
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="quiet_hours_start"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Quiet Hours Start</FormLabel>
                      <FormControl>
                        <Input type="time" {...field} />
                      </FormControl>
                      <FormDescription>
                        Start time for quiet hours
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="quiet_hours_end"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Quiet Hours End</FormLabel>
                      <FormControl>
                        <Input type="time" {...field} />
                      </FormControl>
                      <FormDescription>
                        End time for quiet hours
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="timezone"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Timezone</FormLabel>
                    <FormControl>
                      <Input placeholder="UTC" {...field} />
                    </FormControl>
                    <FormDescription>
                      Your timezone for notification timing
                    </FormDescription>
                    <FormMessage />
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
