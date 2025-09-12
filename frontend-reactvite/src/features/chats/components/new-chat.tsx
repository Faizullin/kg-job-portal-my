import { useEffect, useState } from "react";
import { Check, X } from "lucide-react";
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
import { type ChatUser } from "../data/chat-types";
import type { DialogControl } from "@/hooks/use-dialog-control";
import { useQuery, useMutation } from "@tanstack/react-query";
import myApi from "@/lib/api/my-api";
import type { ChatRoom } from "@/lib/api/axios-client/api";

type User = Omit<ChatUser, "messages">;

type NewChatProps = {
  users?: User[];
  control?: DialogControl;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  onCreated?: (room: ChatRoom) => void;
  orderId?: number; // Optional order to attach to the chat
};

export function NewChat({ users, onOpenChange, open, control, onCreated, orderId }: NewChatProps) {
  const [selectedUsers, setSelectedUsers] = useState<User[]>([]);
  const [search, setSearch] = useState("");

  // Load users from backend if not provided
  const { data: fetchedUsers = [] } = useQuery({
    queryKey: ["chat-user-search", search],
    queryFn: async () => {
      if (users && users.length > 0) return users;
      const res = await myApi.v1UsersList({ search, pageSize: 20 });
      const results = (res.data as any).results || res.data || [];
      const authData = myApi.getAuthData();
      const currentUserId = authData?.user?.id ? String(authData.user.id) : null;
      return results
        .filter((u: any) => String(u.id) !== currentUserId)
        .map((u: any) => ({
          id: String(u.id),
          profile: u.photo_url || u.photo || "",
          username: u.username || u.email || String(u.id),
          fullName: u.name || `${u.first_name || ""} ${u.last_name || ""}`.trim() || u.username,
          title: "",
        })) as User[];
    },
  });

  const createRoomMutation = useMutation({
    mutationFn: async () => {
      const participantIds = selectedUsers.map((u) => Number(u.id)).filter((n) => !Number.isNaN(n));
      const title = selectedUsers.map((u) => u.fullName).join(", ");
      const response = await myApi.v1ChatRoomsCreateCreate({
        chatRoomCreate: {
          title: title || (orderId ? 'Order Chat' : 'New Chat'),
          chat_type: orderId ? 'order_chat' : 'general_chat',
          is_active: true,
          participants: participantIds,
          ...(orderId && { order: orderId })
        }
      })
      return response.data;
    },
    onSuccess: (room) => {
      if (onCreated) onCreated(room as any);
      if (control) control.hide();
      setSelectedUsers([]);
    },
  });

  const handleSelectUser = (user: User) => {
    if (!selectedUsers.find((u) => u.id === user.id)) {
      setSelectedUsers([...selectedUsers, user]);
    } else {
      handleRemoveUser(user.id);
    }
  };

  const handleRemoveUser = (userId: string) => {
    setSelectedUsers(selectedUsers.filter((user) => user.id !== userId));
  };

  const isOpen = control ? control.isVisible : !!open;
  const handleOpenChange = (next: boolean) => {
    if (control) {
      next ? control.show() : control.hide();
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
                {user.fullName}
                <button
                  className="ring-offset-background focus:ring-ring ms-1 rounded-full outline-hidden focus:ring-2 focus:ring-offset-2"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleRemoveUser(user.id);
                    }
                  }}
                  onClick={() => handleRemoveUser(user.id)}
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
                {(fetchedUsers || []).map((user) => (
                  <CommandItem
                    key={user.id}
                    onSelect={() => handleSelectUser(user)}
                    className="hover:bg-accent hover:text-accent-foreground flex items-center justify-between gap-2"
                  >
                    <div className="flex items-center gap-2">
                      <img
                        src={user.profile || "/placeholder.svg"}
                        alt={user.fullName}
                        className="h-8 w-8 rounded-full"
                      />
                      <div className="flex flex-col">
                        <span className="text-sm font-medium">
                          {user.fullName}
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
