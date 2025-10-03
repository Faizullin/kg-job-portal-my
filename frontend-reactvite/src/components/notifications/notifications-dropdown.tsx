import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Bell, Check, X } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import myApi from "@/lib/api/my-api";
import { format } from "date-fns";
import { toast } from "sonner";

const NOTIFICATIONS_QUERY_KEY = 'notifications';

interface NotificationsDropdownProps {
  className?: string;
}

export function NotificationsDropdown({ className }: NotificationsDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const queryClient = useQueryClient();

  // Fetch notifications
  const notificationsQuery = useQuery({
    queryKey: [NOTIFICATIONS_QUERY_KEY],
    queryFn: async () => {
      const response = await myApi.v1NotificationsList({
        ordering: '-created_at',
        pageSize: 20,
      });
      return response.data;
    },
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refetch every minute
  });

  // Mark notification as read
  const markReadMutation = useMutation({
    mutationFn: async (id: string) => {
      return myApi.v1NotificationsMarkRead({
        id,
        notificationRequest: {
          title: "",
          message: "",
          verb: "read"
        }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_QUERY_KEY] });
    },
    onError: (error) => {
      console.error('Failed to mark notification as read:', error);
    }
  });

  // Mark all notifications as read
  const markAllReadMutation = useMutation({
    mutationFn: async () => {
      return myApi.v1NotificationsMarkAllRead({
        notificationRequest: {
          title: "",
          message: "",
          verb: "read_all"
        }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_QUERY_KEY] });
      toast.success("All notifications marked as read");
    },
    onError: (error) => {
      console.error('Failed to mark all notifications as read:', error);
      toast.error("Failed to mark notifications as read");
    }
  });

  // Delete notification
  const deleteNotificationMutation = useMutation({
    mutationFn: async (id: string) => {
      return myApi.v1NotificationsDestroy({ id });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_QUERY_KEY] });
    },
    onError: (error) => {
      console.error('Failed to delete notification:', error);
      toast.error("Failed to delete notification");
    }
  });

  const notifications = notificationsQuery.data?.results || [];
  const unreadCount = notifications.filter(n => !n.is_read).length;

  const formatNotificationDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffTime / (1000 * 60));

    if (diffMinutes < 1) {
      return "Just now";
    } else if (diffMinutes < 60) {
      return `${diffMinutes}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays === 1) {
      return "Yesterday";
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return format(date, "MMM d");
    }
  };

  const handleMarkAsRead = async (notificationId: string) => {
    markReadMutation.mutate(notificationId);
  };

  const handleDeleteNotification = async (notificationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    deleteNotificationMutation.mutate(notificationId);
  };

  const handleMarkAllRead = () => {
    markAllReadMutation.mutate();
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className={`relative ${className}`}>
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
            >
              {unreadCount > 99 ? '99+' : unreadCount}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent 
        className="w-80 p-0" 
        align="end"
        sideOffset={8}
      >
        <div className="p-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-sm">Notifications</h3>
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleMarkAllRead}
                disabled={markAllReadMutation.isPending}
                className="text-xs h-6 px-2"
              >
                Mark all read
              </Button>
            )}
          </div>
        </div>
        
        <Separator />
        
        <ScrollArea className="h-80">
          {notificationsQuery.isLoading ? (
            <div className="p-4 space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="animate-pulse space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No notifications</p>
            </div>
          ) : (
            <div className="p-2">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-3 rounded-lg cursor-pointer transition-colors hover:bg-gray-50 ${
                    !notification.is_read ? 'bg-blue-50 border-l-2 border-l-blue-500' : ''
                  }`}
                  onClick={() => !notification.is_read && handleMarkAsRead(notification.id.toString())}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {notification.title}
                      </p>
                      <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {formatNotificationDate(notification.created_at)}
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-1">
                      {!notification.is_read && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMarkAsRead(notification.id.toString());
                          }}
                          className="h-6 w-6 p-0 hover:bg-green-100"
                          disabled={markReadMutation.isPending}
                        >
                          <Check className="h-3 w-3 text-green-600" />
                        </Button>
                      )}
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => handleDeleteNotification(notification.id.toString(), e)}
                        className="h-6 w-6 p-0 hover:bg-red-100"
                        disabled={deleteNotificationMutation.isPending}
                      >
                        <X className="h-3 w-3 text-red-600" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
        
        {notifications.length > 0 && (
          <>
            <Separator />
            <div className="p-2">
              <Button variant="ghost" size="sm" className="w-full text-xs">
                View all notifications
              </Button>
            </div>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
