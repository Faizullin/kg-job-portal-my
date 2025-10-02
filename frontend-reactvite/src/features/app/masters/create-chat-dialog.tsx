import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import myApi from "@/lib/api/my-api";
import type { ChatRoomCreate, ChatParticipant } from "@/lib/api/axios-client/api";
import { useMutation } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/auth-store";
import { useState } from "react";
import { toast } from "sonner";
import { useNavigate } from "@tanstack/react-router";

interface CreateChatDialogProps {
  isOpen: boolean;
  onClose: () => void;
  masterId: number;
  masterName: string;
}

export function CreateChatDialog({ isOpen, onClose, masterId, masterName }: CreateChatDialogProps) {
  const [message, setMessage] = useState("");
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const createChatMutation = useMutation({
    mutationFn: async (chatData: ChatRoomCreate) => {
      const response = await myApi.v1ChatsRoomsCreate(chatData);
      return response.data;
    },
    onSuccess: (chatRoom) => {
      toast.success("Чат создан успешно!");
      onClose();
      setMessage("");
      // Navigate to the chat room using search params
      navigate({ to: '/chats', search: { chatId: chatRoom.id?.toString() } });
    },
    onError: (error: any) => {
      toast.error("Ошибка при создании чата");
      console.error("Chat creation error:", error);
    }
  });

  const handleCreateChat = () => {
    if (!user?.id) {
      toast.error("Пользователь не авторизован");
      return;
    }

    if (!message.trim()) {
      toast.error("Введите сообщение");
      return;
    }

    const participants: ChatParticipant[] = [
      {
        user: user.id,
        role: "client",
        is_active: true,
        joined_at: new Date().toISOString(),
        last_read_at: new Date().toISOString(),
        notifications_enabled: true,
        is_typing: false,
        is_online: true
      },
      {
        user: masterId,
        role: "master",
        is_active: true,
        joined_at: new Date().toISOString(),
        last_read_at: new Date().toISOString(),
        notifications_enabled: true,
        is_typing: false,
        is_online: false
      }
    ];

    const chatData: ChatRoomCreate = {
      name: `Чат с ${masterName}`,
      description: `Личный чат с мастером ${masterName}`,
      participants: participants,
      chat_type: "job_chat",
      is_active: true,
      created_at: new Date().toISOString()
    };

    createChatMutation.mutate(chatData);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Создать чат с мастером</DialogTitle>
          <DialogDescription>
            Напишите сообщение мастеру {masterName} для начала общения
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="message">Ваше сообщение</Label>
            <Textarea
              id="message"
              placeholder="Напишите сообщение мастеру..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="min-h-[100px]"
            />
          </div>
        </div>

        <DialogFooter className="flex gap-2">
          <Button variant="outline" onClick={onClose}>
            Отмена
          </Button>
          <Button 
            onClick={handleCreateChat}
            disabled={createChatMutation.isPending || !message.trim()}
          >
            {createChatMutation.isPending ? "Создание..." : "Создать чат"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
