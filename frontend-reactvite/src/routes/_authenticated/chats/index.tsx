import { Chats } from "@/features/chats";
import { createFileRoute } from "@tanstack/react-router";

type ChatSearch = {
  chat_room_id: number | undefined
}

export const Route = createFileRoute("/_authenticated/chats/")({
  component: Chats,
  validateSearch: (search: Record<string, unknown>): ChatSearch => {
    return {
      chat_room_id: (search.chat_room_id as number) || undefined,
    };
  },
});
