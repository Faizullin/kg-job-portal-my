import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ChatTypeEnum, type ChatRoomCreate } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useAuthStore } from "@/stores/auth-store";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";

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
      const response = await myApi.v1ChatsRoomsCreate({
        chatRoomCreateRequest: chatData
      });
      return response.data;
    },
    onSuccess: (chatRoom) => {
      toast.success("Чат создан успешно!");
      onClose();
      setMessage("");
      // Navigate to the chat room using search params
      navigate({ to: '/chats', search: { chat_room_id: chatRoom.id, } });
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

    const chatData = {
      title: `Чат с ${masterName}`,
      chat_type: ChatTypeEnum.job_chat,
      participants_users_ids: [user.id, masterId],
    };

    createChatMutation.mutate(chatData as any);
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
