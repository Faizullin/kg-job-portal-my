import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { DialogControl } from "@/hooks/use-dialog-control";
import { ChatRoomCreateChatTypeEnum, type ChatConversation, type UserList } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useAuthStore } from "@/stores/auth-store";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

type NewChatProps = {
  control?: DialogControl;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  onCreated?: (room: ChatConversation) => void;
  orderId?: number; // Optional order to attach to the chat
};

export function NewChat({ onOpenChange, open, control, onCreated, orderId }: NewChatProps) {
  const [selectedUsers, setSelectedUsers] = useState<UserList[]>([]);
  const [search, setSearch] = useState("");
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const loadChatUserSearchQuery = useQuery({
    queryKey: ["chat-user-search", search],
    queryFn: () => {
      return myApi.v1UsersList({
        search,
        pageSize: 20
      })
    },
  });

  const users = useMemo(() => {
    if (!user?.id) return [];
    return (loadChatUserSearchQuery.data?.data?.results || [])
      .filter((u) => String(u.id) !== String(user.id))
  }, [loadChatUserSearchQuery.data, user]);

  const createRoomMutation = useMutation({
    mutationFn: async () => {
      if (selectedUsers.length === 0) throw new Error('No users selected');

      // Create chat room using the backend API
      // const response = await myApi.axios.post('/api/v1/chat/conversations/create/', {
      //   title: selectedUsers.map((u) => u.username).join(", ") || (orderId ? 'Order Chat' : 'New Chat'),
      //   chat_type: orderId ? 'order_chat' : 'general_chat',
      //   participants: selectedUsers.map(u => u.id),
      //   ...(orderId && { order_id: orderId })
      // });
      const response = await myApi.v1ChatConversationsCreateCreate({
        chatRoomCreate: {
          title: selectedUsers.map((u) => u.username).join(", ") || (orderId ? 'Order Chat' : 'New Chat'),
          chat_type: orderId ? ChatRoomCreateChatTypeEnum.order_chat : ChatRoomCreateChatTypeEnum.general_chat,
          participants: selectedUsers.map(u => u.id),
          ...(orderId && { order_id: orderId })
        }
      });

      // Convert ChatRoom response to ChatConversation format
      const chatRoom = response.data;
      const firstUser = selectedUsers[0];

      const conversation: ChatConversation = {
        id: chatRoom.id,
        title: chatRoom.title,
        chat_type: chatRoom.chat_type as any,
        other_participant_name: firstUser.username,
        other_participant_avatar: firstUser.photo_url || '',
        other_participant_online: 'false',
        last_message_preview: '',
        last_message_time: '',
        service_category: '',
        unread_count: '0',
        is_active: chatRoom.is_active,
        created_at: chatRoom.created_at
      };

      return conversation;
    },
    onSuccess: (room) => {
      queryClient.invalidateQueries({ queryKey: ['chat-rooms'] });
      if (onCreated) onCreated(room);
      if (control) control.hide();
      setSelectedUsers([]);
    },
  });

  const handleSelectUser = (user: UserList) => {
    if (!selectedUsers.find((u) => Number(u.id) === Number(user.id))) {
      setSelectedUsers([...selectedUsers, user]);
    } else {
      handleRemoveUser(user);
    }
  };

  const handleRemoveUser = useCallback((user: UserList) => {
    setSelectedUsers(selectedUsers.filter((u) => Number(u.id) !== Number(user.id)));
  }, [selectedUsers]);

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
          <DialogTitle>{orderId ? 'New order chat' : 'New message'}</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col gap-4">
          <div className="flex flex-wrap items-baseline-last gap-2">
            <span className="text-muted-foreground min-h-6 text-sm">To:</span>
            {selectedUsers.map((user) => (
              <Badge key={user.id} variant="default">
                {user.username}
                <button
                  className="ring-offset-background focus:ring-ring ms-1 rounded-full outline-hidden focus:ring-2 focus:ring-offset-2"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleRemoveUser(user);
                    }
                  }}
                  onClick={() => handleRemoveUser(user)}
                >
                  <X className="text-muted-foreground hover:text-foreground h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
          <Command className="rounded-lg border">
            <CommandInput
              placeholder="Search people..."
              className="text-foreground"
              onValueChange={(v) => setSearch(v)}
            />
            <CommandList>
              <CommandEmpty>No people found.</CommandEmpty>
              <CommandGroup>
                {(users || []).map((user) => (
                  <CommandItem
                    key={user.id}
                    onSelect={() => handleSelectUser(user)}
                    className="hover:bg-accent hover:text-accent-foreground flex items-center justify-between gap-2"
                  >
                    <div className="flex items-center gap-2">
                      <img
                        src={user.photo_url || "/placeholder.svg"}
                        alt={user.username}
                        className="h-8 w-8 rounded-full"
                      />
                      <div className="flex flex-col">
                        <span className="text-sm font-medium">
                          {user.username}
                        </span>
                        <span className="text-accent-foreground/70 text-xs">
                          {user.username}
                        </span>
                      </div>
                    </div>

                    {selectedUsers.find((u) => u.id === user.id) && (
                      <Check className="h-4 w-4" />
                    )}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
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
