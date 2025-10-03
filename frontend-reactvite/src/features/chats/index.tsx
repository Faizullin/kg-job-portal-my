import { ConfigDrawer } from "@/components/config-drawer";
import { DeleteConfirmNiceDialog } from "@/components/dialogs/delete-confirm-dialog";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import NiceModal from "@/components/nice-modal/modal-context";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { Search } from "@/components/search";
import { ThemeSwitch } from "@/components/theme-switch";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { CUrls } from "@/config/constants";
import { useDialogControl } from "@/hooks/use-dialog-control";
import { MessageCreateMessageTypeEnum, MessageMessageTypeEnum, type ChatRoom, type ChatRoomCreate, type Message } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useSearch } from "@tanstack/react-router";
import { format } from "date-fns";
import {
  ArrowLeft,
  Edit,
  File,
  FileImage,
  ImagePlus,
  MessagesSquare,
  MoreVertical,
  Paperclip,
  Phone,
  Plus,
  Search as SearchIcon,
  Send,
  Trash2,
  Video,
} from "lucide-react";
import { Fragment, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { NewChatDialog } from "./components/new-chat";

// Query keys
const CHAT_ROOMS_QUERY_KEY = 'chat-rooms';
const CHAT_MESSAGES_QUERY_KEY = 'chat-messages';

export function Chats() {
  const searchParams = useSearch({ from: "/_authenticated/chats/" });
  const [search, setSearch] = useState("");
  const [selectedRoom, setSelectedRoom] = useState<ChatRoomCreate | null>(null);
  const [mobileSelectedRoom, setMobileSelectedRoom] = useState<ChatRoomCreate | null>(null);
  const newChatControl = useDialogControl();
  const [messageInput, setMessageInput] = useState("");
  const messageInputRef = useRef<HTMLInputElement>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const auth = useAuthStore();

  // Context menu state
  const [contextMenu, setContextMenu] = useState<{
    visible: boolean;
    x: number;
    y: number;
    message: Message | null;
  }>({
    visible: false,
    x: 0,
    y: 0,
    message: null,
  });

  const handleContextMenu = useCallback((e: React.MouseEvent, message: Message) => {
    e.preventDefault();
    setContextMenu({
      visible: true,
      x: e.clientX,
      y: e.clientY,
      message: message,
    });
  }, []);

  const hideContextMenu = useCallback(() => {
    setContextMenu({
      visible: false,
      x: 0,
      y: 0,
      message: null,
    });
  }, []);

  // Load chat rooms
  const loadChatRoomsQuery = useQuery({
    queryKey: [CHAT_ROOMS_QUERY_KEY],
    queryFn: async () => {
      const response = await myApi.v1ChatsRoomsList({
        ordering: '-last_message_at,-created_at'
      });
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const rooms = useMemo(() => loadChatRoomsQuery.data?.results || [], [loadChatRoomsQuery.data]);

  // Auto-select chat room if chatId is provided in search params
  useEffect(() => {
    const chatId = searchParams.chat_room_id;
    if (chatId && rooms.length > 0 && !selectedRoom) {
      const room = rooms.find(r => r.id?.toString() === chatId.toString());
      if (room) {
        setSelectedRoom(room);
        setMobileSelectedRoom(room);
      }
    }
  }, [searchParams.chat_room_id, rooms, selectedRoom]);

  // Single WebSocket connection for receiving messages
  useEffect(() => {
    if (!selectedRoom?.id || !auth.token) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
        setIsConnected(false);
        setConnectionError(null);
      }
      return;
    }

    // Close existing connection if switching rooms
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Create new WebSocket connection
    const ws = new WebSocket(`${CUrls.WS_CHAT_URL}/ws/chat/${selectedRoom.id}/?token=${auth.token}`);

    ws.onopen = () => {
      setIsConnected(true);
      setConnectionError(null);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'chat_message' && data.message_id) {
          // Update query cache with new message
          queryClient.setQueryData<Message[]>([CHAT_MESSAGES_QUERY_KEY, selectedRoom.id], (oldData) => {
            if (!oldData) return oldData;
            console.log('🔍 [Messages] New oldData:', oldData);

            // Determine message type from WebSocket data
            let messageType = MessageMessageTypeEnum.text;
            if (data.message_type === 'image') {
              messageType = MessageMessageTypeEnum.image;
            } else if (data.message_type === 'file') {
              messageType = MessageMessageTypeEnum.file;
            } else if (data.message_type === 'system') {
              messageType = MessageMessageTypeEnum.system;
            }

            // Process attachments from WebSocket
            const processedAttachments = data.attachments ? data.attachments.map((attachment: any) => ({
              id: attachment.id || 0,
              original_filename: attachment.name || 'attachment',
              file_url: attachment.url || '',
              size: attachment.size || 0,
              file_type: attachment.type || 'file',
              created_at: new Date().toISOString()
            })) : [];

            const newMessage: Message = {
              id: data.message_id,
              chat_room: selectedRoom.id,
              sender: {
                id: data.sender?.id || 0,
                username: data.sender?.full_name || 'Unknown',
                email: '',
                first_name: '',
                last_name: '',
                photo_url: ''
              },
              content: data.content || '',
              message_type: messageType,
              attachments: processedAttachments,
              reply_to: null,
              reply_to_sender: '',
              is_read: false,
              read_at: null,
              created_at: data.created_at || new Date().toISOString(),
              updated_at: data.updated_at || new Date().toISOString(),
            };

            return [...(oldData), newMessage]; // Append new message to bottom
          });
        } else if (data.type === 'message_deleted' && data.message_id) {
          // Remove deleted message from cache
          queryClient.setQueryData<Message[]>([CHAT_MESSAGES_QUERY_KEY, selectedRoom.id], (oldData) => {
            if (!oldData) return oldData;
            return oldData.filter(msg => msg.id !== data.message_id);
          });
        }
      } catch (error) {
        console.error('WebSocket message parse error:', error);
      }
    };

    ws.onclose = () => setIsConnected(false);
    ws.onerror = () => {
      setConnectionError('WebSocket connection error');
      setIsConnected(false);
    };

    wsRef.current = ws;

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [selectedRoom?.id, auth.token, queryClient]);

  const loadChatMessagesQuery = useQuery({
    queryKey: [CHAT_MESSAGES_QUERY_KEY, selectedRoom?.id],
    queryFn: async () => {
      if (!selectedRoom?.id) return [];
      const response = await myApi.v1ChatsRoomsMessagesList({
        chatRoomId: String(selectedRoom.id),
        ordering: 'created_at', // Oldest first, so latest messages appear at bottom
        pageSize: 50
      });
      console.log('🔍 [Messages] New response.data:', response.data);
      return response.data.results || [];
    },
    enabled: !!selectedRoom?.id,
    staleTime: 2 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 3,
    retryDelay: 1000,
  });

  const messages = useMemo(() => {
    const rawMessages = loadChatMessagesQuery.data || [];
    console.log('🔍 [Messages] Messages with names:', rawMessages);

    return rawMessages.map((message) => {
      const isOwnMessage = message.sender.id === auth.user?.id;
      const senderName = isOwnMessage ? "You" : (
        message.sender.first_name && message.sender.last_name
          ? `${message.sender.first_name} ${message.sender.last_name}`.trim()
          : message.sender.username || 'Unknown'
      );

      return {
        ...message,
        senderName,
        isOwnMessage,
      };
    });
  }, [loadChatMessagesQuery.data, auth.user]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Mutation for sending messages via HTTP
  const sendMessageMutation = useMutation({
    mutationFn: async ({ content, attachment, message_type }: {
      content: string;
      attachment?: File;
      message_type: MessageCreateMessageTypeEnum;
    }) => {
      if (!selectedRoom) throw new Error('No room selected');

      // If there's an attachment, use FormData with direct axios call
      if (attachment) {
        const formData = new FormData();
        formData.append('content', content);
        formData.append('message_type', message_type);
        formData.append('attachments_files[]', attachment);

        const response = await myApi.axios.post(
          `/api/v1/chats/rooms/${selectedRoom.id}/messages/`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          }
        );
        return response;
      }

      // For text messages without attachments, use the regular API
      return myApi.v1ChatsRoomsMessagesCreate({
        chatRoomId: String(selectedRoom.id),
        messageCreateRequest: {
          content: content,
          message_type: message_type,
        }
      });
    },
    onSuccess: () => {
      setMessageInput('');
      messageInputRef.current?.focus();
      // Don't invalidate queries - let WebSocket handle real-time updates
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    },
    onError: (error: any) => {
      console.error('Failed to send message:', error);
      const errorMessage = error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Failed to send message';
      alert(`Error: ${errorMessage}`);
    }
  });

  // Mutation for deleting chat room
  const deleteRoomMutation = useMutation({
    mutationFn: async (roomId: string) => {
      return myApi.v1ChatsRoomsDestroy({ id: roomId });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CHAT_ROOMS_QUERY_KEY] });
      setSelectedRoom(null);
      setMobileSelectedRoom(null);
    },
    onError: (error) => {
      console.error('Failed to delete chat room:', error);
    }
  });

  // Mutation for deleting messages
  const deleteMessageMutation = useMutation({
    mutationFn: async (messageId: string) => {
      if (!selectedRoom?.id) throw new Error('No room selected');
      return myApi.v1ChatsRoomsMessagesDestroy({
        chatRoomId: String(selectedRoom.id),
        id: messageId
      });
    },
    onError: (error: any) => {
      console.error('Failed to delete message:', error);

      const errorMessage = error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Failed to delete message';
      alert(`Error: ${errorMessage}`);
    }
  });

  const handleDeleteRoom = useCallback(async () => {
    if (!selectedRoom?.id) return;

    const result = await NiceModal.show(DeleteConfirmNiceDialog, {
      args: {
        title: "Delete Chat",
        desc: "Are you sure you want to delete this chat? This action cannot be undone.",
      }
    });

    if (result.reason === "confirm") {
      deleteRoomMutation.mutate(String(selectedRoom.id));
    }
  }, [selectedRoom?.id, deleteRoomMutation]);

  const handleDeleteMessage = useCallback(async (message: Message) => {
    if (!message.id) return;

    const result = await NiceModal.show(DeleteConfirmNiceDialog, {
      args: {
        title: "Delete Message",
        desc: "Are you sure you want to delete this message? This action cannot be undone.",
      }
    });

    if (result.reason === "confirm") {
      deleteMessageMutation.mutate(String(message.id));
    }
  }, [deleteMessageMutation]);

  const sendMessage = useCallback((content: string) => {
    if (!selectedRoom || !content.trim()) return;
    sendMessageMutation.mutate({
      content: content.trim(),
      message_type: MessageCreateMessageTypeEnum.text,
    });
  }, [selectedRoom, sendMessageMutation]);

  const sendAttachment = useCallback((file: File) => {
    if (!selectedRoom) return;

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      alert('File size too large. Maximum size is 10MB.');
      return;
    }

    const messageType = file.type.startsWith('image/')
      ? MessageCreateMessageTypeEnum.image
      : MessageCreateMessageTypeEnum.file;

    // Generate appropriate content based on file type
    let content = '';
    if (file.type.startsWith('image/')) {
      content = '📷 Image';
    } else if (file.type.startsWith('video/')) {
      content = '🎥 Video';
    } else if (file.type.startsWith('audio/')) {
      content = '🎵 Audio';
    } else if (file.type.includes('pdf')) {
      content = '📄 PDF Document';
    } else if (file.type.includes('word') || file.type.includes('document')) {
      content = '📝 Document';
    } else {
      content = '📎 File';
    }

    sendMessageMutation.mutate({
      content: content,
      message_type: messageType,
      attachment: file,
    });
  }, [selectedRoom, sendMessageMutation]);

  const handleImageUpload = useCallback(() => {
    imageInputRef.current?.click();
  }, []);

  const handleFileUpload = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleImageChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      sendAttachment(file);
    }
    // Reset input
    event.target.value = '';
  }, [sendAttachment]);

  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      sendAttachment(file);
    }
    // Reset input
    event.target.value = '';
  }, [sendAttachment]);

  const handleRoomSelect = useCallback((room: ChatRoom) => {
    setSelectedRoom(room);
    setMobileSelectedRoom(room);
  }, []);

  const handleSendMessage = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (!messageInput.trim() || !selectedRoom) return;

    const content = messageInput.trim();
    sendMessage(content);
  }, [messageInput, selectedRoom, sendMessage]);

  // Filtered chat list (memoized for performance)
  const filteredChatList = useMemo(() => {
    return rooms.filter((room: ChatRoom) =>
      (room.title || '').toLowerCase().includes(search.trim().toLowerCase()) ||
      room.participants.some(p => p.user.username.toLowerCase().includes(search.trim().toLowerCase()))
    );
  }, [rooms, search]);

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
              {loadChatRoomsQuery.isLoading ? (
                <div className="flex items-center justify-center p-4">
                  <div className="text-sm text-muted-foreground">Loading chats...</div>
                </div>
              ) : loadChatRoomsQuery.error ? (
                <div className="flex items-center justify-center p-4">
                  <div className="text-sm text-red-500">Failed to load chats</div>
                </div>
              ) : filteredChatList.length === 0 ? (
                <div className="flex items-center justify-center p-4">
                  <div className="text-sm text-muted-foreground">No chats found</div>
                </div>
              ) : filteredChatList.map((room) => {
                const displayTitle = room.title || `Chat #${room.id}`;
                const lastMsg = "No messages yet"; // TODO: Add last message preview from API
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
                      <AvatarFallback>{(selectedRoom.title || 'C').charAt(0).toUpperCase()}</AvatarFallback>
                    </Avatar>
                    <div>
                      <span className="col-start-2 row-span-2 text-sm font-medium lg:text-base">{selectedRoom.title || `Chat #${selectedRoom.id}`}</span>
                      <span className="text-muted-foreground col-start-2 row-span-2 row-start-2 line-clamp-1 block max-w-32 text-xs text-nowrap text-ellipsis lg:max-w-none lg:text-sm">
                        {selectedRoom.chat_type || 'Chat'}
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
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button size="icon" variant="ghost" className="h-10 rounded-md sm:h-8 sm:w-4 lg:h-10 lg:w-6">
                        <MoreVertical className="stroke-muted-foreground sm:size-5" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={handleDeleteRoom}
                        className="text-destructive focus:text-destructive"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete Chat
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>

              <div className="flex flex-1 flex-col gap-2 rounded-md px-4 pt-0 pb-4">
                <div className="flex size-full flex-1">
                  <div className="chat-text-container relative -me-4 flex flex-1 flex-col overflow-y-hidden">
                    <div className="chat-flex flex h-40 w-full grow flex-col justify-start gap-4 overflow-y-auto py-2 pe-4 pb-4">
                      {loadChatMessagesQuery.isLoading ? (
                        <div className="flex items-center justify-center p-4">
                          <div className="text-sm text-muted-foreground">Loading messages...</div>
                        </div>
                      ) : connectionError ? (
                        <div className="flex flex-col items-center justify-center p-4 gap-2">
                          <div className="text-sm text-red-500">
                            WebSocket Error: {connectionError}
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setConnectionError(null);
                              // Force reconnection by updating auth token dependency
                              if (wsRef.current) {
                                wsRef.current.close();
                              }
                            }}
                          >
                            Reconnect
                          </Button>
                        </div>
                      ) : loadChatMessagesQuery.error ? (
                        <div className="flex flex-col items-center justify-center p-4 gap-2">
                          <div className="text-sm text-red-500">
                            Failed to load messages: {loadChatMessagesQuery.error.message || 'Unknown error'}
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => loadChatMessagesQuery.refetch()}
                            disabled={loadChatMessagesQuery.isFetching}
                          >
                            {loadChatMessagesQuery.isFetching ? 'Retrying...' : 'Retry'}
                          </Button>
                        </div>
                      ) : messages.length === 0 ? (
                        <div className="flex items-center justify-center p-4">
                          <div className="text-sm text-muted-foreground">No messages yet. Start chatting!</div>
                        </div>
                      ) : messages.map((msg, index) => (
                        <div
                          key={`${msg.id}-${index}`}
                          className={cn("chat-box max-w-72 px-3 py-2 break-words shadow-lg", msg.isOwnMessage ? "bg-primary/90 text-primary-foreground/75 self-end rounded-[16px_16px_0_16px]" : "bg-muted self-start rounded-[16px_16px_16px_0]")}
                          onContextMenu={msg.isOwnMessage ? (e) => handleContextMenu(e, msg) : undefined}
                        >
                          {/* Handle different message types */}
                          {msg.message_type === 'image' && msg.attachments?.[0]?.file_url ? (
                            <div className="mb-2">
                              <img
                                src={msg.attachments[0].file_url}
                                alt="Chat image"
                                className="max-w-full h-auto max-h-64 rounded-lg cursor-pointer"
                                onClick={() => window.open(msg.attachments[0].file_url, '_blank')}
                              />
                              {msg.content && !msg.content.startsWith('📷') && (
                                <div className="mt-2">{msg.content}</div>
                              )}
                            </div>
                          ) : msg.message_type === 'file' && msg.attachments?.[0]?.file_url ? (
                            <div className="mb-2">
                              <div className="p-2 bg-muted/50 rounded-lg">
                                <div className="flex items-center gap-2">
                                  <Paperclip className="h-4 w-4" />
                                  <div className="flex-1">
                                    <div className="text-sm font-medium">
                                      {msg.attachments[0].original_filename || 'File'}
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                      {Math.round((msg.attachments[0].size || 0) / 1024)} KB
                                    </div>
                                  </div>
                                  <a
                                    href={msg.attachments[0].file_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs text-blue-600 hover:underline"
                                  >
                                    Download
                                  </a>
                                </div>
                              </div>
                              {msg.content && !msg.content.startsWith('📎') && !msg.content.startsWith('📄') && !msg.content.startsWith('📝') && !msg.content.startsWith('🎥') && !msg.content.startsWith('🎵') && (
                                <div className="mt-2">{msg.content}</div>
                              )}
                            </div>
                          ) : msg.message_type === 'system' ? (
                            <div className="text-center text-xs text-muted-foreground italic">
                              {msg.content}
                            </div>
                          ) : (
                            /* Regular text message */
                            <div>{msg.content}</div>
                          )}
                          <span className={cn("text-foreground/75 mt-1 block text-xs font-light italic", msg.isOwnMessage && "text-primary-foreground/85 text-end")}>{format(new Date(msg.created_at), "h:mm a")}</span>
                        </div>
                      ))}
                      <div ref={messagesEndRef} />
                    </div>
                  </div>
                </div>
                <form onSubmit={handleSendMessage} className="flex w-full flex-none gap-2">
                  <div className="border-input bg-card focus-within:ring-ring flex flex-1 items-center gap-2 rounded-md border px-2 py-1 focus-within:ring-1 focus-within:outline-hidden lg:gap-4">
                    <div className="space-x-1">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button size="icon" type="button" variant="ghost" className="h-8 rounded-md">
                            <Plus size={20} className="stroke-muted-foreground" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="start">
                          <DropdownMenuItem onClick={handleImageUpload}>
                            <FileImage className="mr-2 h-4 w-4" />
                            Upload Image
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={handleFileUpload}>
                            <File className="mr-2 h-4 w-4" />
                            Upload File
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                      <Button size="icon" type="button" variant="ghost" className="hidden h-8 rounded-md lg:inline-flex" onClick={handleImageUpload}><ImagePlus size={20} className="stroke-muted-foreground" /></Button>
                      <Button size="icon" type="button" variant="ghost" className="hidden h-8 rounded-md lg:inline-flex" onClick={handleFileUpload}><Paperclip size={20} className="stroke-muted-foreground" /></Button>
                    </div>
                    <label className="flex-1">
                      <span className="sr-only">Chat Text Box</span>
                      <input ref={messageInputRef} type="text" placeholder={isConnected ? "Type your messages..." : "Connecting..."} value={messageInput} onChange={(e) => setMessageInput(e.target.value)} className="h-8 w-full bg-inherit focus-visible:outline-hidden" />
                    </label>
                    <Button
                      type="submit"
                      variant="ghost"
                      size="icon"
                      className="hidden sm:inline-flex"
                      disabled={sendMessageMutation.isPending}
                    >
                      {sendMessageMutation.isPending ? (
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                      ) : (
                        <Send size={20} />
                      )}
                    </Button>
                  </div>
                  <Button
                    type="submit"
                    className="h-full sm:hidden"
                    disabled={sendMessageMutation.isPending}
                  >
                    {sendMessageMutation.isPending ? (
                      <div className="flex items-center gap-2">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                        <span>Sending...</span>
                      </div>
                    ) : (
                      <>
                        <Send size={18} />
                        <span>Send</span>
                      </>
                    )}
                  </Button>
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
        <NewChatDialog
          control={newChatControl}
          onCreated={(room) => {
            setSelectedRoom(room);
            setMobileSelectedRoom(room);
          }} />

        {/* Hidden file inputs for attachments */}
        <input
          ref={imageInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          className="hidden"
        />
        <input
          ref={fileInputRef}
          type="file"
          accept="*/*"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Context Menu for Message Actions */}
        {contextMenu.visible && contextMenu.message && (
          <div
            className="fixed z-50 bg-background border border-border rounded-md shadow-lg py-1 min-w-32"
            style={{
              left: contextMenu.x,
              top: contextMenu.y,
            }}
          >
            <button
              className="flex w-full items-center px-3 py-2 text-sm text-destructive hover:bg-destructive/10"
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteMessage(contextMenu.message!);
                hideContextMenu();
              }}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete Message
            </button>
          </div>
        )}

        {/* Click outside to hide context menu */}
        {contextMenu.visible && (
          <div
            className="fixed inset-0 z-40"
            onClick={hideContextMenu}
          />
        )}
      </Main>
    </>
  );
}
