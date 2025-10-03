import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { TopNav } from "@/components/layout/top-nav";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { ThemeSwitch } from "@/components/theme-switch";
import { ConfigDrawer } from "@/components/config-drawer";
import { NotificationsDropdown } from "@/components/notifications/notifications-dropdown";
import { NewJobsTab } from "./jobs-tabs/new-jobs-tab";
import { InProgressTab } from "./jobs-tabs/in-progress-tab";
import { HistoryTab } from "./jobs-tabs/history-tab";
import myApi from "@/lib/api/my-api";
import { useAuthStore } from "@/stores/auth-store";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  DollarSign,
  MapPin,
  Clock,
  Filter
} from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";

const MASTER_DASHBOARD_QUERY_KEY = 'master-dashboard';

export function MasterDashboard() {
  const [activeTab, setActiveTab] = useState("new");
  const queryClient = useQueryClient();
  const { user } = useAuthStore();

  // Fetch master profile data
  const masterProfileQuery = useQuery({
    queryKey: [MASTER_DASHBOARD_QUERY_KEY, 'profile'],
    queryFn: async () => {
      const response = await myApi.v1UsersMyMasterRetrieve();
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });



  // Online status mutation
  const onlineStatusMutation = useMutation({
    mutationFn: async (isOnline: boolean) => {
      return myApi.v1UsersMastersUpdateOnlineStatus({
        masterOnlineStatusRequestRequest: {
          is_online: isOnline
        }
      });
    },
    onSuccess: (response) => {
      const newStatus = response.data.is_online;
      queryClient.setQueryData([MASTER_DASHBOARD_QUERY_KEY, 'profile'], (oldData: any) => ({
        ...oldData,
        is_online: newStatus
      }));
      toast.success(newStatus ? "You are now online" : "You are now offline");
    },
    onError: (error) => {
      console.error('Failed to update online status:', error);
      toast.error("Failed to update online status");
    }
  });

  const handleOnlineToggle = (online: boolean) => {
    onlineStatusMutation.mutate(online);
  };

  // Get master profile data with fallbacks
  const masterProfile = useMemo(() => masterProfileQuery.data || null, [masterProfileQuery.data]);
  const masterName = useMemo(() => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user?.username || "";
  }, [user]);
  const masterLocation = masterProfile?.current_location || "";
  const masterAvatar = user?.photo_url;
  const isOnline = (masterProfile as any)?.is_online ?? false;


  // Handle error state
  if (masterProfileQuery.error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-red-600">Ошибка загрузки</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Не удалось загрузить данные дашборда
          </p>
          <Button
            onClick={() => queryClient.invalidateQueries({ queryKey: [MASTER_DASHBOARD_QUERY_KEY] })}
            className="mt-4"
          >
            Попробовать снова
          </Button>
        </div>
      </div>
    );
  }

  return (
    <>
      <Header>
        <TopNav links={masterTopNav} />
        <div className="ms-auto flex items-center space-x-4">
          <NotificationsDropdown />
          <ThemeSwitch />
          <ConfigDrawer />
          <ProfileDropdown />
        </div>
      </Header>

      <Main>
        <div className="space-y-6">
          {/* Mobile Header */}
          <div className="bg-blue-600 text-white p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Avatar className="h-12 w-12">
                  <AvatarImage src={masterAvatar || undefined} alt={masterName} />
                  <AvatarFallback className="text-lg">{masterName.charAt(0).toUpperCase()}</AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium text-lg">Добрый день, {masterName}</p>
                  <div className="flex items-center space-x-1 mt-1">
                    <div className="w-2 h-2 bg-blue-300 rounded-full"></div>
                    <p className="text-sm opacity-90">{masterLocation}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Online Status */}
          <Card className="border border-gray-200">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-500' : 'bg-gray-400'}`} />
                    <span className="font-medium text-base">{isOnline ? 'Онлайн' : 'Офлайн'}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {isOnline ? 'Принимаете заказы' : 'Не принимаете заказы'}
                  </p>
                </div>
                <Switch
                  checked={isOnline}
                  onCheckedChange={handleOnlineToggle}
                  disabled={onlineStatusMutation.isPending}
                  className="data-[state=checked]:bg-green-600"
                />
              </div>
            </CardContent>
          </Card>

          {/* Filter Bar */}
          <Card className="border border-gray-200">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3 overflow-x-auto">
                <Button variant="outline" size="sm" className="flex items-center space-x-2 whitespace-nowrap border-gray-300 hover:bg-gray-50">
                  <DollarSign className="h-4 w-4" />
                  <span>Цена</span>
                </Button>
                <Button variant="outline" size="sm" className="flex items-center space-x-2 whitespace-nowrap border-gray-300 hover:bg-gray-50">
                  <MapPin className="h-4 w-4" />
                  <span>Расстояние</span>
                </Button>
                <Button variant="outline" size="sm" className="flex items-center space-x-2 whitespace-nowrap border-gray-300 hover:bg-gray-50">
                  <Clock className="h-4 w-4" />
                  <span>Время</span>
                </Button>
                <Button variant="outline" size="sm" className="flex items-center space-x-2 whitespace-nowrap border-gray-300 hover:bg-gray-50 ml-auto">
                  <Filter className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="new">Новые</TabsTrigger>
              <TabsTrigger value="in_progress">В работе</TabsTrigger>
              <TabsTrigger value="history">История</TabsTrigger>
            </TabsList>

            <TabsContent value="new" className="space-y-4">
              <NewJobsTab />
            </TabsContent>

            <TabsContent value="in_progress" className="space-y-4">
              <InProgressTab />
            </TabsContent>

            <TabsContent value="history" className="space-y-4">
              <HistoryTab />
            </TabsContent>
          </Tabs>
        </div>
      </Main>
    </>
  );
}

const masterTopNav = [
  {
    title: "Главная",
    href: "/app/master",
    isActive: true,
    disabled: false,
  },
  {
    title: "Заявки",
    href: "/app/requests",
    isActive: false,
    disabled: false,
  },
  {
    title: "Сообщения",
    href: "/app/chats",
    isActive: false,
    disabled: false,
  },
  {
    title: "Мои заказы",
    href: "/app/orders",
    isActive: false,
    disabled: false,
  },
  {
    title: "Профиль",
    href: "/app/profile",
    isActive: false,
    disabled: false,
  },
];