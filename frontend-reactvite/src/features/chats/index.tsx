import { ConfigDrawer } from "@/components/config-drawer";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { Search } from "@/components/search";
import { ThemeSwitch } from "@/components/theme-switch";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useDialogControl } from "@/hooks/use-dialog-control";
import type { ChatConversation, PaginatedChatConversationList, ChatConversationDetail } from "@/lib/api/axios-client/api";
import { MessageTypeEnum } from "@/lib/api/axios-client/api";

// Define Message interface since it's not properly generated
interface Message {
  id: number;
  chat_room: number;
  sender: number;
  sender_name: string;
  content: string;
  message_type: 'text' | 'image' | 'file';
  message_type_display: string;
  attachment?: string | null;
  attachment_name?: string | null;
  attachment_size?: number | null;
  is_read: boolean;
  read_at?: string | null;
  created_at: string;
}
import myApi from "@/lib/api/my-api";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosResponse } from "axios";
import { format } from "date-fns";
import {
  ArrowLeft,
  Edit,
  ImagePlus,
  MessagesSquare,
  MoreVertical,
  Paperclip,
  Phone,
  Plus,
  Search as SearchIcon,
  Send,
  Video,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Fragment } from "react/jsx-runtime";
import { NewChat } from "./components/new-chat";
import { useMutation } from "@tanstack/react-query";

export function Chats() {
  const [search, setSearch] = useState("");
  const [selectedRoom, setSelectedRoom] = useState<ChatConversation | null>(null);
  const [mobileSelectedRoom, setMobileSelectedRoom] = useState<ChatConversation | null>(null);
  const newChatControl = useDialogControl();
  const [messageInput, setMessageInput] = useState("");
  const messageInputRef = useRef<HTMLInputElement>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const auth = useAuthStore();

  const { data: roomsData, isLoading: roomsLoading } = useQuery<AxiosResponse<PaginatedChatConversationList>>({
    queryKey: ['chat-rooms'],
    queryFn: () => myApi.v1ChatConversationsList({ ordering: '-last_message_at,-created_at' }),
  });
  const rooms: ChatConversation[] = roomsData?.data?.results || [];

  // Load messages only on initial room selection
  const { data: messagesData, isLoading: messagesLoading } = useQuery<AxiosResponse<ChatConversationDetail>>({
    queryKey: ['chat-messages', selectedRoom?.id],
    queryFn: () => myApi.v1ChatConversationsRetrieve({ id: selectedRoom!.id }),
    enabled: !!selectedRoom?.id,
    staleTime: Infinity, // Never refetch automatically after initial load
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  });
  const messages: Message[] = Array.isArray(messagesData?.data?.messages) ? messagesData.data.messages : [];

  // Mutation for sending messages with attachments
  const sendMessageMutation = useMutation({
    mutationFn: async ({ content, attachment }: { content?: string; attachment?: File }) => {
      if (!selectedRoom) throw new Error('No room selected');
      
      const formData = new FormData();
      if (content) formData.append('message', content);
      if (attachment) {
        formData.append('attachment', attachment);
        formData.append('message_type', 'image');
      }
      
      return myApi.v1ChatConversationsSendCreate({
        id: selectedRoom.id,
        chatSendMessage: {
          message: content || '',
          message_type: attachment ? MessageTypeEnum.image : MessageTypeEnum.text,
          attachment: attachment ? attachment.name : undefined
        }
      });
    },
    onSuccess: () => {
      // Message will be received via WebSocket
      setMessageInput('');
    },
    onError: (error) => {
      console.error('Failed to send message:', error);
    }
  });

  const sendMessage = (content: string) => {
    if (!selectedRoom || !content.trim()) return;

    console.log('📤 [API] Sending message:', content);
    sendMessageMutation.mutate({ content: content.trim() });
    messageInputRef.current?.focus();
  };

  const sendImage = (file: File) => {
    if (!selectedRoom) return;

    console.log('📤 [API] Sending image:', file.name);
    sendMessageMutation.mutate({ attachment: file });
  };

  const handleImageUpload = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      sendImage(file);
    }
    // Reset input
    event.target.value = '';
  };

  useEffect(() => {
    const connectWebSocket = (roomId: number) => {
      console.log('🔌 [WebSocket] Attempting to connect to chat room:', roomId);
      const token = useAuthStore.getState().token;
      try {
        if (!token) {
          console.error('❌ [WebSocket] No authentication token available');
          setConnectionError('Authentication required');
          return;
        }

        const wsUrl = `${import.meta.env.VITE_BACKEND_API_URL.replace('http', 'ws')}/ws/chat/${roomId}/?token=${token}`;
        console.log('🌐 [WebSocket] Connecting to:', wsUrl);

        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
          console.log('✅ [WebSocket] Connection established to room:', roomId);
          setIsConnected(true);
          setConnectionError(null);
        };

        wsRef.current.onmessage = (event) => {
          console.log('📨 [WebSocket] Received message:', event.data);

          try {
            const data = JSON.parse(event.data);
            console.log('📋 [WebSocket] Parsed data:', data);

            switch (data.type) {
              case 'connection_established':
                console.log('🎉 [WebSocket] Connection confirmed for user:', data.user_id, 'in room:', data.room_id);
                break;

              case 'chat_message':
                if (data.message_id) {
                  console.log('💬 [WebSocket] Processing chat message from:', data.sender_name, 'content:', data.message);

                  const newMessage: Message = {
                    id: data.message_id,
                    chat_room: roomId,
                    sender: data.sender_id || 0,
                    sender_name: data.sender_name || 'Unknown',
                    content: data.message || '',
                    message_type: data.message_type || 'text',
                    message_type_display: data.message_type === 'image' ? 'Image' : 'Text',
                    attachment: data.attachment_url || null,
                    attachment_name: data.attachment_name || null,
                    attachment_size: data.attachment_size || null,
                    is_read: false,
                    read_at: null,
                    created_at: data.timestamp || new Date().toISOString(),
                  };

                  // Update query cache with new message
                  queryClient.setQueryData<AxiosResponse<ChatConversationDetail>>(['chat-messages', roomId], (oldData) => {
                    if (!oldData) {
                      return oldData;
                    }

                    // For now, just invalidate the query to refetch
                    queryClient.invalidateQueries({ queryKey: ['chat-messages', roomId] });
                    return oldData;
                  });
                  console.log('📝 [WebSocket] Added new message to cache:', newMessage.id);
                }
                break;

              case 'error':
                console.error('❌ [WebSocket] Server error:', data.message);
                setConnectionError(data.message || 'Server error occurred');
                break;

              default:
                console.warn('⚠️ [WebSocket] Unknown message type:', data.type, 'data:', data);
            }
          } catch (err) {
            console.error('❌ [WebSocket] Failed to parse message:', err, 'raw data:', event.data);
          }
        };

        wsRef.current.onclose = (event) => {
          console.log('🔌 [WebSocket] Connection closed with code:', event.code, 'reason:', event.reason);
          setIsConnected(false);

          if (event.code === 4001) {
            console.error('🚫 [WebSocket] Unauthorized access - invalid token');
            setConnectionError('Authentication failed');
          } else if (event.code === 4003) {
            console.error('🚫 [WebSocket] Forbidden - no access to room');
            setConnectionError('No access to this chat room');
          } else if (event.code !== 1000) {
            console.error('⚠️ [WebSocket] Unexpected disconnection');
            setConnectionError('Connection lost');
          }
        };

        wsRef.current.onerror = (error) => {
          console.error('❌ [WebSocket] Connection error:', error);
          setIsConnected(false);
          setConnectionError('Failed to connect to chat server');
        };

      } catch (err) {
        console.error('❌ [WebSocket] Connection setup error:', err);
        setConnectionError('Failed to establish connection');
      }
    };
    const disconnectWebSocket = () => {
      if (wsRef.current) {
        console.log('🔌 [WebSocket] Disconnecting from room:', selectedRoom?.id);
        wsRef.current.close(1000, 'User disconnected');
        wsRef.current = null;
      }

      setIsConnected(false);
      setConnectionError(null);
    };
    if (selectedRoom) {
      connectWebSocket(selectedRoom.id);
    } else {
      // disconnectWebSocket();
    }
    return () => {
      disconnectWebSocket();
    };
  }, [selectedRoom, queryClient]);

  const handleRoomSelect = (room: ChatConversation) => {
    console.log('🏠 [Chat] Selecting room:', room.id, 'title:', room.title || room.other_participant_name);
    setSelectedRoom(room);
    setMobileSelectedRoom(room);
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageInput.trim() || !selectedRoom) return;

    const content = messageInput.trim();
    sendMessage(content);
  };

  const filteredChatList = rooms.filter((room: ChatConversation) =>
    (room.title || '').toLowerCase().includes(search.trim().toLowerCase()) ||
    (room.other_participant_name || '').toLowerCase().includes(search.trim().toLowerCase())
  );

  const currentMessage = messages.reduce(
    (acc: Record<string, { sender: string; message: string; timestamp: string; message_type?: string; attachment?: string }[]>, message: Message) => {
      const key = format(new Date(message.created_at), "d MMM, yyyy");
      if (!acc[key]) acc[key] = [];
      const isOwnMessage = message.sender === auth.user?.id;
      acc[key].push({
        sender: isOwnMessage ? "You" : (message.sender_name || 'Unknown'),
        message: message.content,
        timestamp: message.created_at,
        message_type: message.message_type,
        attachment: message.attachment || undefined,
      });
      return acc;
    },
    {},
  );

  return (
    <>
      <Header>
        <Search />
        <div className="ms-auto flex items-center space-x-4">
          <ThemeSwitch />
          <ConfigDrawer />
          <ProfileDropdown />
        </div>
      </Header>

      <Main fixed>
        <section className="flex h-full gap-6">
          <div className="flex w-full flex-col gap-2 sm:w-56 lg:w-72 2xl:w-80">
            <div className="bg-background sticky top-0 z-10 -mx-4 px-4 pb-3 shadow-md sm:static sm:z-auto sm:mx-0 sm:p-0 sm:shadow-none">
              <div className="flex items-center justify-between py-2">
                <div className="flex gap-2">
                  <h1 className="text-2xl font-bold">Inbox</h1>
                  <MessagesSquare size={20} />
                </div>

                <Button size="icon" variant="ghost" onClick={() => newChatControl.show()} className="rounded-lg">
                  <Edit size={24} className="stroke-muted-foreground" />
                </Button>
              </div>

              <label className={cn("focus-within:ring-ring focus-within:ring-1 focus-within:outline-hidden", "border-border flex h-10 w-full items-center space-x-0 rounded-md border ps-2",)}>
                <SearchIcon size={15} className="me-2 stroke-slate-500" />
                <span className="sr-only">Search</span>
                <input type="text" className="w-full flex-1 bg-inherit text-sm focus-visible:outline-hidden" placeholder="Search chat..." value={search} onChange={(e) => setSearch(e.target.value)} />
              </label>
            </div>

            <ScrollArea className="-mx-3 h-full overflow-scroll p-3">
              {roomsLoading ? (
                <div className="flex items-center justify-center p-4"><div className="text-sm text-muted-foreground">Loading chats...</div></div>
              ) : filteredChatList.length === 0 ? (
                <div className="flex items-center justify-center p-4"><div className="text-sm text-muted-foreground">No chats found</div></div>
              ) : filteredChatList.map((room) => {
                const displayTitle = room.title || room.other_participant_name || `Chat #${room.id}`;
                const lastMsg = room.last_message_preview || "No messages yet";
                return (
                  <Fragment key={room.id}>
                    <button type="button" className={cn("group hover:bg-accent hover:text-accent-foreground", "flex w-full rounded-md px-2 py-2 text-start text-sm", selectedRoom?.id === room.id && "sm:bg-muted",)} onClick={() => handleRoomSelect(room)}>
                      <div className="flex gap-2">
                        <Avatar>
                          <AvatarFallback>{displayTitle.charAt(0).toUpperCase()}</AvatarFallback>
                        </Avatar>
                        <div>
                          <span className="col-start-2 row-span-2 font-medium">{displayTitle}</span>
                          <span className="text-muted-foreground group-hover:text-accent-foreground/90 col-start-2 row-span-2 row-start-2 line-clamp-2 text-ellipsis">{lastMsg}</span>
                        </div>
                      </div>
                    </button>
                    <Separator className="my-1" />
                  </Fragment>
                );
              })}
            </ScrollArea>
          </div>

          {selectedRoom ? (
            <div className={cn("bg-background absolute inset-0 start-full z-50 hidden w-full flex-1 flex-col border shadow-xs sm:static sm:z-auto sm:flex sm:rounded-md", mobileSelectedRoom && "start-0 flex",)}>
              <div className="bg-card mb-1 flex flex-none justify-between p-4 shadow-lg sm:rounded-t-md">
                <div className="flex gap-3">
                  <Button size="icon" variant="ghost" className="-ms-2 h-full sm:hidden" onClick={() => setMobileSelectedRoom(null)}>
                    <ArrowLeft className="rtl:rotate-180" />
                  </Button>
                  <div className="flex items-center gap-2 lg:gap-4">
                    <Avatar className="size-9 lg:size-11">
                      <AvatarFallback>{(selectedRoom.title || selectedRoom.other_participant_name || 'C').charAt(0).toUpperCase()}</AvatarFallback>
                    </Avatar>
                    <div>
                      <span className="col-start-2 row-span-2 text-sm font-medium lg:text-base">{selectedRoom.title || selectedRoom.other_participant_name || `Chat #${selectedRoom.id}`}</span>
                      <span className="text-muted-foreground col-start-2 row-span-2 row-start-2 line-clamp-1 block max-w-32 text-xs text-nowrap text-ellipsis lg:max-w-none lg:text-sm">
                        {selectedRoom.chat_type}
                        {isConnected && <span className="text-green-500 ml-1" title="Connected">●</span>}
                        {connectionError && <span className="text-red-500 ml-1" title={connectionError}>●</span>}
                        {!isConnected && !connectionError && <span className="text-yellow-500 ml-1" title="Connecting...">●</span>}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="-me-1 flex items-center gap-1 lg:gap-2">
                  <Button size="icon" variant="ghost" className="hidden size-8 rounded-full sm:inline-flex lg:size-10"><Video size={22} className="stroke-muted-foreground" /></Button>
                  <Button size="icon" variant="ghost" className="hidden size-8 rounded-full sm:inline-flex lg:size-10"><Phone size={22} className="stroke-muted-foreground" /></Button>
                  <Button size="icon" variant="ghost" className="h-10 rounded-md sm:h-8 sm:w-4 lg:h-10 lg:w-6"><MoreVertical className="stroke-muted-foreground sm:size-5" /></Button>
                </div>
              </div>

              <div className="flex flex-1 flex-col gap-2 rounded-md px-4 pt-0 pb-4">
                <div className="flex size-full flex-1">
                  <div className="chat-text-container relative -me-4 flex flex-1 flex-col overflow-y-hidden">
                    <div className="chat-flex flex h-40 w-full grow flex-col-reverse justify-start gap-4 overflow-y-auto py-2 pe-4 pb-4">
                      {messagesLoading ? (
                        <div className="flex items-center justify-center p-4"><div className="text-sm text-muted-foreground">Loading messages...</div></div>
                      ) : messages.length === 0 ? (
                        <div className="flex items-center justify-center p-4"><div className="text-sm text-muted-foreground">No messages yet. Start chatting!</div></div>
                      ) : currentMessage && Object.keys(currentMessage).map((key) => (
                        <Fragment key={key}>
                          {currentMessage[key].map((msg, index) => (
                            <div key={`${msg.sender}-${msg.timestamp}-${index}`} className={cn("chat-box max-w-72 px-3 py-2 break-words shadow-lg", msg.sender === "You" ? "bg-primary/90 text-primary-foreground/75 self-end rounded-[16px_16px_0_16px]" : "bg-muted self-start rounded-[16px_16px_16px_0]")}>
                              {msg.message_type === 'image' && msg.attachment ? (
                                <div className="mb-2">
                                  <img 
                                    src={msg.attachment} 
                                    alt="Chat image" 
                                    className="max-w-full h-auto rounded-lg cursor-pointer"
                                    onClick={() => window.open(msg.attachment, '_blank')}
                                  />
                                </div>
                              ) : null}
                              {msg.message}{" "}
                              <span className={cn("text-foreground/75 mt-1 block text-xs font-light italic", msg.sender === "You" && "text-primary-foreground/85 text-end")}>{format(new Date(msg.timestamp), "h:mm a")}</span>
                            </div>
                          ))}
                          <div className="text-center text-xs">{key}</div>
                        </Fragment>
                      ))}
                    </div>
                  </div>
                </div>
                <form onSubmit={handleSendMessage} className="flex w-full flex-none gap-2">
                  <div className="border-input bg-card focus-within:ring-ring flex flex-1 items-center gap-2 rounded-md border px-2 py-1 focus-within:ring-1 focus-within:outline-hidden lg:gap-4">
                    <div className="space-x-1">
                      <Button size="icon" type="button" variant="ghost" className="h-8 rounded-md"><Plus size={20} className="stroke-muted-foreground" /></Button>
                      <Button size="icon" type="button" variant="ghost" className="hidden h-8 rounded-md lg:inline-flex" onClick={handleImageUpload}><ImagePlus size={20} className="stroke-muted-foreground" /></Button>
                      <Button size="icon" type="button" variant="ghost" className="hidden h-8 rounded-md lg:inline-flex"><Paperclip size={20} className="stroke-muted-foreground" /></Button>
                    </div>
                    <label className="flex-1">
                      <span className="sr-only">Chat Text Box</span>
                      <input ref={messageInputRef} type="text" placeholder={isConnected ? "Type your messages..." : "Connecting..."} value={messageInput} onChange={(e) => setMessageInput(e.target.value)} className="h-8 w-full bg-inherit focus-visible:outline-hidden" />
                    </label>
                    <Button type="submit" variant="ghost" size="icon" className="hidden sm:inline-flex"><Send size={20} /></Button>
                  </div>
                  <Button type="submit" className="h-full sm:hidden"><Send size={18} /> Send</Button>
                </form>
              </div>
            </div>
          ) : (
            <div className={cn("bg-card absolute inset-0 start-full z-50 hidden w-full flex-1 flex-col justify-center rounded-md border shadow-xs sm:static sm:z-auto sm:flex",)}>
              <div className="flex flex-col items-center space-y-6">
                <div className="border-border flex size-16 items-center justify-center rounded-full border-2"><MessagesSquare className="size-8" /></div>
                <div className="space-y-2 text-center">
                  <h1 className="text-xl font-semibold">Your messages</h1>
                  <p className="text-muted-foreground text-sm">Send a message to start a chat.</p>
                </div>
                <Button onClick={() => newChatControl.show()}>Send message</Button>
              </div>
            </div>
          )}
        </section>
        <NewChat control={newChatControl} onCreated={(room) => { setSelectedRoom(room); setMobileSelectedRoom(room); }} />
        
        {/* Hidden file input for image uploads */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />
      </Main>
    </>
  );
}
