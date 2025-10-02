import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { TopNav } from "@/components/layout/top-nav";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { ThemeSwitch } from "@/components/theme-switch";
import { ConfigDrawer } from "@/components/config-drawer";
import myApi from "@/lib/api/my-api";
import { useAuthStore } from "@/stores/auth-store";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Job } from "@/lib/api/axios-client/api";
import { Status30eEnum } from "@/lib/api/axios-client/api";
import {
  Bell,
  Menu,
  DollarSign,
  MapPin,
  Clock,
  Filter,
  Calendar,
  ChevronRight
} from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";

const MASTER_DASHBOARD_QUERY_KEY = 'master-dashboard';

export function MasterDashboard() {
  const [isOnline, setIsOnline] = useState(true);
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

  // Fetch job requests based on status
  const jobRequestsQuery = useQuery({
    queryKey: [MASTER_DASHBOARD_QUERY_KEY, 'requests', activeTab],
    queryFn: async () => {
      let status: Status30eEnum | undefined;

      switch (activeTab) {
        case 'new':
          status = Status30eEnum.published;
          break;
        case 'in_progress':
          status = Status30eEnum.in_progress;
          break;
        case 'history':
          status = Status30eEnum.completed;
          break;
        default:
          status = undefined;
      }

      const response = await myApi.v1SearchJobsList({
        ordering: '-created_at',
        page: 1,
        pageSize: 20,
        status: status
      });
      return response.data.results;
    },
    staleTime: 30 * 1000,
  });

  // Online status mutation
  const onlineStatusMutation = useMutation({
    mutationFn: async (online: boolean) => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return online;
    },
    onSuccess: (online) => {
      setIsOnline(online);
      toast.success(online ? "Вы онлайн" : "Вы офлайн");
    },
    onError: () => {
      toast.error("Ошибка при обновлении статуса");
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

  const jobRequests = useMemo(() => jobRequestsQuery.data || [], [jobRequestsQuery.data]);


  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return `Сегодня, ${date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (diffDays === 1) {
      return `Завтра, ${date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (diffDays === 2) {
      return `Послезавтра, ${date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`;
    } else {
      return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  };

  const getStatusBadge = (status: Job['status'] | undefined) => {
    switch (status) {
      case Status30eEnum.published:
        return <Badge className="bg-blue-100 text-blue-800">Новый</Badge>;
      case Status30eEnum.in_progress:
        return <Badge className="bg-yellow-100 text-yellow-800">В работе</Badge>;
      case Status30eEnum.completed:
        return <Badge className="bg-green-100 text-green-800">Завершен</Badge>;
      case Status30eEnum.cancelled:
        return <Badge className="bg-red-100 text-red-800">Отменен</Badge>;
      case Status30eEnum.assigned:
        return <Badge className="bg-purple-100 text-purple-800">Назначен</Badge>;
      case Status30eEnum.draft:
        return <Badge className="bg-gray-100 text-gray-800">Черновик</Badge>;
      default:
        return null;
    }
  };

  // Handle error state
  if (masterProfileQuery.error || jobRequestsQuery.error) {
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
          <Button variant="ghost" size="sm" className="relative">
            <Bell className="h-5 w-5" />
            <div className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-red-500 text-xs text-white flex items-center justify-center">
              3
            </div>
          </Button>
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
              <div className="flex items-center space-x-3">
                <Button variant="ghost" size="sm" className="text-white hover:bg-blue-700 p-2">
                  <Bell className="h-5 w-5" />
                </Button>
                <Button variant="ghost" size="sm" className="text-white hover:bg-blue-700 p-2">
                  <Menu className="h-5 w-5" />
                </Button>
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

            <TabsContent value={activeTab} className="space-y-4">
              {jobRequestsQuery.isLoading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <Card key={i}>
                      <CardContent className="p-4">
                        <div className="animate-pulse space-y-3">
                          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                          <div className="h-3 bg-gray-200 rounded w-1/4"></div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : jobRequests.length === 0 ? (
                <Card>
                  <CardContent className="p-8 text-center">
                    <p className="text-muted-foreground">
                      {activeTab === 'new' && 'Нет новых заявок'}
                      {activeTab === 'in_progress' && 'Нет заявок в работе'}
                      {activeTab === 'history' && 'История пуста'}
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  {jobRequests.map((request) => (
                    <Card key={request.id} className="hover:shadow-md transition-shadow border border-gray-200">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <h3 className="font-semibold text-lg flex-1">{request.title}</h3>
                          <div className="ml-2">
                            {getStatusBadge(request.status)}
                          </div>
                        </div>

                        <div className="text-blue-600 font-semibold text-lg mb-3">
                          {request.budget_min && request.budget_max 
                            ? `${request.budget_min.toLocaleString()} - ${request.budget_max.toLocaleString()} тг`
                            : request.final_price 
                            ? `${request.final_price.toLocaleString()} тг`
                            : 'Цена договорная'
                          }
                        </div>

                        <div className="space-y-2 mb-4">
                          {request.service_date && (
                            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                              <Calendar className="h-4 w-4" />
                              <span>{formatDate(request.service_date)}</span>
                            </div>
                          )}
                          {request.location && (
                            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                              <MapPin className="h-4 w-4" />
                              <span>{request.location}</span>
                            </div>
                          )}
                        </div>

                        <Button 
                          className="w-full bg-blue-600 hover:bg-blue-700 text-white" 
                          variant={request.status === Status30eEnum.published ? 'default' : 'outline'}
                        >
                          Подробнее
                          <ChevronRight className="ml-2 h-4 w-4" />
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
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