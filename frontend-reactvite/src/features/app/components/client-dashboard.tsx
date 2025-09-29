import { ConfigDrawer } from "@/components/config-drawer";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { TopNav } from "@/components/layout/top-nav";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { ThemeSwitch } from "@/components/theme-switch";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useDebounce } from "@/hooks/use-debounce";
import myApi from "@/lib/api/my-api";
import { useAuthStore } from "@/stores/auth-store";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import {
  ArrowRight,
  Bell,
  Clock,
  Heart,
  Home,
  MapPin,
  MessageCircle,
  MoreHorizontal,
  Plus,
  Search as SearchIcon,
  Settings,
  Sparkles,
  Star,
  Users,
  Wrench,
  Zap
} from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";


const CLIENT_DASHBOARD_QUERY_KEY = 'client-dashboard';

export function ClientDashboard() {
  const [searchQuery, setSearchQuery] = useState("");
  const [favoriteMasters, setFavoriteMasters] = useState<Set<number>>(new Set());
  const debouncedSearch = useDebounce(searchQuery, 300);
  const queryClient = useQueryClient();

  // Fetch client dashboard data from backend
  const { data: dashboardData, isLoading, error } = useQuery({
    queryKey: [CLIENT_DASHBOARD_QUERY_KEY, debouncedSearch],
    queryFn: async () => {
      const response = await myApi.v1DashboardMyClientRetrieve();
      return response.data;
    },
    retry: 2,
  });

  const { user } = useAuthStore();

  // Handle error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-red-600">Ошибка загрузки</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Не удалось загрузить данные дашборда
          </p>
          <Button
            onClick={() => queryClient.invalidateQueries({ queryKey: [CLIENT_DASHBOARD_QUERY_KEY] })}
            className="mt-4"
          >
            Попробовать снова
          </Button>
        </div>
      </div>
    );
  }

  // Extract data from backend response
  const backendFeaturedCategories = dashboardData?.featured_categories || [];
  const topMasters = dashboardData?.top_providers || [];

  // Favorite master mutation
  const favoriteMutation = useMutation({
    mutationFn: async (masterId: number) => {
      // This would be a real API call to favorite/unfavorite a master
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call
      return masterId;
    },
    onSuccess: (masterId) => {
      setFavoriteMasters(prev => {
        const newSet = new Set(prev);
        if (newSet.has(masterId)) {
          newSet.delete(masterId);
          toast.success("Удалено из избранного");
        } else {
          newSet.add(masterId);
          toast.success("Добавлено в избранное");
        }
        return newSet;
      });
    },
    onError: () => {
      toast.error("Ошибка при обновлении избранного");
    }
  });

  const handleFavoriteMaster = (masterId: number) => {
    favoriteMutation.mutate(masterId);
  };

  const iconMap = {
    'wrench': Wrench,
    'home': Home,
    'zap': Zap,
    'settings': Settings,
    'users': Users,
    'plus': Plus,
    'sparkles': Sparkles,
    'clock': Clock,
    'message': MessageCircle,
  };

  const getIcon = (iconName: string) => {
    return iconMap[iconName as keyof typeof iconMap] || Settings;
  };

  // Use backend categories or fallback to mock data
  const featuredCategories = backendFeaturedCategories.length > 0 ? backendFeaturedCategories : [
    { id: 1, name: "Ремонт", icon: "wrench", color: "bg-blue-500", description: "23000" },
    { id: 2, name: "Уборка", icon: "home", color: "bg-green-500", description: "19300" },
    { id: 3, name: "Сад", icon: "sparkles", color: "bg-emerald-500", description: "8500" },
    { id: 4, name: "Сантехника", icon: "zap", color: "bg-blue-600", description: "12000" },
    { id: 5, name: "Электрика", icon: "zap", color: "bg-yellow-500", description: "9800" },
    { id: 6, name: "Отделка", icon: "home", color: "bg-purple-500", description: "15600" },
  ];

  // Use auth store user info
  const displayUserInfo = useMemo(() => {
    if (user) {
      const full_name = user.first_name && user.last_name
        ? `${user.first_name} ${user.last_name}`
        : user.username;
      return { name: full_name, location: "Алматы" };
    }

    return { name: "Пользователь", location: "Алматы" };
  }, [user]);

  return (
    <>
      <Header>
        <TopNav links={clientTopNav} />
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
          {/* Welcome Section */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Добрый день, {displayUserInfo.name}</h1>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span>{displayUserInfo.location}</span>
              </div>
            </div>
            <Button variant="outline" size="sm">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>

          {/* Search Bar */}
          <Card>
            <CardContent className="p-4">
              <div className="relative">
                <SearchIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Ввести название услуги/сервиса"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </CardContent>
          </Card>

          {/* Service Categories */}
          <div>
            <h2 className="mb-4 text-lg font-semibold">Вас может заинтересовать</h2>
            {isLoading ? (
              <div className="grid grid-cols-3 gap-4 sm:grid-cols-6">
                {[...Array(6)].map((_, i) => (
                  <Card key={i} className="animate-pulse">
                    <CardContent className="flex flex-col items-center space-y-2 p-4">
                      <div className="rounded-full p-3 bg-gray-300 h-12 w-12"></div>
                      <div className="h-4 bg-gray-300 rounded w-16"></div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-3 gap-4 sm:grid-cols-6">
                {featuredCategories.map((category: any) => {
                  const IconComponent = getIcon(category.icon || 'settings');
                  return (
                    <Card key={category.id} className="cursor-pointer transition-all hover:shadow-md group">
                      <CardContent className="flex flex-col items-center space-y-2 p-4">
                        <div className={`rounded-full p-3 ${category.color || 'bg-gray-500'} group-hover:scale-110 transition-transform`}>
                          <IconComponent className="h-6 w-6 text-white" />
                        </div>
                        <div className="text-center">
                          <span className="text-sm font-medium block">{category.name}</span>
                          <span className="text-xs text-muted-foreground">{category.description}</span>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>


          {/* Top Specialists */}
          <div>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Топ специалистов</h2>
              <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-700" asChild>
                <Link to="/app/service-providers">
                  Видеть всех
                  <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </Button>
            </div>
            {isLoading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <Card key={i} className="animate-pulse">
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-3">
                        <div className="h-12 w-12 bg-gray-300 rounded-full"></div>
                        <div className="flex-1 space-y-2">
                          <div className="h-4 bg-gray-300 rounded w-32"></div>
                          <div className="h-3 bg-gray-300 rounded w-24"></div>
                          <div className="h-3 bg-gray-300 rounded w-20"></div>
                        </div>
                        <div className="h-8 bg-gray-300 rounded w-16"></div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                {topMasters.map((master) => {
                  const userData = master.user_profile.user;
                  const userFullName = userData.first_name && userData.last_name
                    ? `${userData.first_name} ${userData.last_name}`
                    : userData.username;
                  return (
                    <Card key={master.id} className="transition-all hover:shadow-md group">
                      <CardContent className="p-4">
                        <div className="flex items-center space-x-3">
                          <div className="relative">
                            <Link to={`/app/service-providers/${master.id}`} className="cursor-pointer">
                              <Avatar className="h-12 w-12">
                                <AvatarImage src={userData.photo_url || "/images/avatar.png"} alt={`${userData.first_name} ${userData.last_name}`} />
                                <AvatarFallback className="bg-blue-100 text-blue-600">
                                  {userFullName}
                                </AvatarFallback>
                              </Avatar>
                            </Link>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <h3 className="font-medium">
                                {userFullName}
                              </h3>
                              <span className="text-sm text-muted-foreground">
                                {master.profession?.name}
                              </span>
                            </div>
                            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                              <div className="flex items-center space-x-1">
                                <Star className="h-3 w-3 fill-yello text-yellow-400" />
                                <span className="font-medium">
                                  {master.statistics?.average_rating || '~'}
                                </span>
                                <span>
                                  ({master.statistics?.total_reviews || "~"} отзывов)
                                </span>
                              </div>
                              <span className="font-medium text-green-600">
                                {master.hourly_rate
                                  ? `${master.hourly_rate}₸/час`
                                  : "Цена договорная"}
                              </span>
                            </div>
                            <div className="flex items-center space-x-2 mt-1">
                              <Clock className="h-3 w-3 text-muted-foreground" />
                              <span className="text-xs text-muted-foreground">
                                Отвечает за {master.response_time_hours || 24} часа
                              </span>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                              Select
                              {/* <Link to={`/app/service-providers/${userData.id}`}>
                                Выбрать
                              </Link> */}
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleFavoriteMaster(userData.id)}
                              className={favoriteMasters.has(userData.id) ? "text-red-500" : "text-muted-foreground"}
                            >
                              <Heart className={`h-4 w-4 ${favoriteMasters.has(userData.id) ? "fill-current" : ""}`} />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            )}
          </div>

          {/* Support Section */}
          <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="rounded-full bg-blue-500 p-2">
                    <MessageCircle className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-medium">Алиса</h3>
                    <p className="text-sm text-muted-foreground">Онлайн тех-поддержка</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-xs text-green-600 font-medium">Онлайн</span>
                </div>
              </div>
              <div className="mt-3">
                <div className="relative">
                  <Input
                    placeholder="Задать свой вопрос..."
                    className="pr-10 bg-white/50 border-blue-200 focus:border-blue-300"
                  />
                  <Button
                    size="sm"
                    className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 bg-blue-500 hover:bg-blue-600"
                  >
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </Main >
    </>
  );
}

const clientTopNav = [
  {
    title: "Главная",
    href: "/app/client",
    isActive: true,
    disabled: false,
  },
  {
    title: "Мастера",
    href: "/app/service-providers",
    isActive: false,
    disabled: false,
  },
  {
    title: "Сообщения",
    href: "/chats",
    isActive: false,
    disabled: false,
  },
  {
    title: "Заказы",
    href: "/jobs",
    isActive: false,
    disabled: false,
  },
  {
    title: "Профиль",
    href: "/settings/profile",
    isActive: false,
    disabled: false,
  },
];
