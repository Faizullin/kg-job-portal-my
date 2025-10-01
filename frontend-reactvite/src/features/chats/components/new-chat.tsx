import ComboBox2 from "@/components/combobox";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { DialogControl } from "@/hooks/use-dialog-control";
import { ChatTypeEnum, type ChatRoomCreate, type Job, type PublicMasterProfile } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useAuthStore } from "@/stores/auth-store";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";

const CHAT_ROOMS_QUERY_KEY = 'chat-rooms';

type NewChatProps = {
  control?: DialogControl;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  onCreated?: (room: ChatRoomCreate) => void;
  job?: Partial<Job>
};

export function NewChat({ onOpenChange, open, control, onCreated, job }: NewChatProps) {
  const [selectedUsers, setSelectedUsers] = useState<PublicMasterProfile[]>([]);
  const queryClient = useQueryClient();
  const { user } = useAuthStore();

  const searchUsers = useCallback(async (search: string, offset: number, limit: number) => {
    if (!user) throw new Error('User not found');
    const response = await myApi.v1UsersMastersList({
      search,
      page: Math.floor(offset / limit) + 1,
      pageSize: limit,
    });
    const mastersList = response.data.results || [];
    return mastersList.filter(i => i.user.id !== user.id)
  }, [user]);

  const createRoomMutation = useMutation({
    mutationFn: async () => {
      if (selectedUsers.length === 0) throw new Error('No users selected');

      const chatRoomCreate: ChatRoomCreate = {
        id: 0, // Will be set by backend
        title: selectedUsers.map((u) => u.user.username).join(", ") || (job ? 'Order Chat' : 'New Chat'),
        chat_type: job ? ChatTypeEnum.job_chat : ChatTypeEnum.general_chat,
        participants_users_ids: selectedUsers.map(u => u.user.id),
        job: job?.id || null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const response = await myApi.v1ChatsRoomsCreate({
        chatRoomCreate
      });

      return response.data;
    },
    onSuccess: (room) => {
      queryClient.invalidateQueries({ queryKey: [CHAT_ROOMS_QUERY_KEY] });
      if (onCreated) onCreated(room);
      if (control) control.hide();
      setSelectedUsers([]);
    },
    onError: (error) => {
      console.error('Failed to create chat room:', error);
    }
  });

  const isOpen = control ? control.isVisible : !!open;
  const handleOpenChange = (next: boolean) => {
    if (control) {
      if (next) {
        control.show();
      } else {
        control.hide();
      }
    } else if (onOpenChange) {
      onOpenChange(next);
    }
  };

  useEffect(() => {
    if (!isOpen) {
      setSelectedUsers([]);
    }
  }, [isOpen]);

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{job ? 'New job chat' : 'New message'}</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Select Users</label>
            <ComboBox2<PublicMasterProfile>
              title="Search and select users..."
              value={selectedUsers}
              valueKey="id"
              multiple={true}
              renderLabel={(user) => (
                <div className="flex items-center gap-2">
                  <Avatar className="h-6 w-6">
                    <AvatarImage
                      src={user.user.photo_url || "/placeholder.svg"}
                      alt={user.user.username}
                    />
                    <AvatarFallback className="text-xs">
                      {user.user.username.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">
                      {user.user.username}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {user.user.first_name} {user.user.last_name}
                    </span>
                  </div>
                </div>
              )}
              searchFn={searchUsers}
              onChange={setSelectedUsers}
              badgeRenderType="outside"
            />
          </div>
          <Button
            variant={"default"}
            onClick={() => createRoomMutation.mutate()}
            disabled={selectedUsers.length === 0 || createRoomMutation.isPending}
          >
            {createRoomMutation.isPending ? "Creating..." : "Create chat"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
