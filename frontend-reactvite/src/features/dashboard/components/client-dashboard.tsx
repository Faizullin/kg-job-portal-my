import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { TopNav } from "@/components/layout/top-nav";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { ThemeSwitch } from "@/components/theme-switch";
import { ConfigDrawer } from "@/components/config-drawer";
import { useDebounce } from "@/hooks/use-debounce";
import myApi from "@/lib/api/my-api";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { 
  Search as SearchIcon, 
  Users, 
  Settings, 
  Plus,
  Star,
  MapPin,
  Heart,
  MoreHorizontal,
  ArrowRight,
  Wrench,
  Home,
  Zap
} from "lucide-react";

interface DashboardData {
  featured_categories?: Array<{
    id: number;
    name: string;
    icon?: string;
    color?: string;
  }>;
  top_providers?: Array<{
    id: number;
    name: string;
    profession: string;
    rating: number;
    reviews_count: number;
    hourly_rate: string;
    is_online: boolean;
    avatar?: string;
    location: string;
  }>;
  action_cards?: Array<{
    title: string;
    description: string;
    icon: string;
    color: string;
    href: string;
  }>;
  user_info?: {
    name: string;
    location: string;
  };
}

export function ClientDashboard() {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearch = useDebounce(searchQuery, 300);

  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboard', 'client', debouncedSearch],
    queryFn: async () => {
      const response = await myApi.axios.get('/api/v1/dashboard/client/');
      return response.data as DashboardData;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const serviceCategories = dashboardData?.featured_categories || [];
  const topMasters = dashboardData?.top_providers || [];
  const actionCards = dashboardData?.action_cards || [];
  const userInfo = dashboardData?.user_info || { name: "Пользователь", location: "Город" };

  const iconMap = {
    'wrench': Wrench,
    'home': Home,
    'zap': Zap,
    'settings': Settings,
    'users': Users,
    'plus': Plus,
  };

  const getIcon = (iconName: string) => {
    return iconMap[iconName as keyof typeof iconMap] || Settings;
  };

  return (
    <>
      <Header>
        <TopNav links={clientTopNav} />
        <div className="ms-auto flex items-center space-x-4">
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
              <h1 className="text-2xl font-bold">Добрый день, {userInfo.name}</h1>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span>{userInfo.location}</span>
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
            <div className="grid grid-cols-3 gap-4 sm:grid-cols-6">
              {serviceCategories.map((category) => {
                const IconComponent = getIcon(category.icon || 'settings');
                return (
                  <Card key={category.id} className="cursor-pointer transition-all hover:shadow-md">
                    <CardContent className="flex flex-col items-center space-y-2 p-4">
                      <div className={`rounded-full p-3 ${category.color || 'bg-gray-500'}`}>
                        <IconComponent className="h-6 w-6 text-white" />
                      </div>
                      <span className="text-center text-sm font-medium">{category.name}</span>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Action Cards */}
          <div className="grid gap-4 sm:grid-cols-3">
            {actionCards.map((card) => {
              const IconComponent = getIcon(card.icon);
              return (
                <Card key={card.title} className="cursor-pointer transition-all hover:shadow-md">
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-3">
                      <div className={`rounded-full p-2 ${card.color}`}>
                        <IconComponent className="h-5 w-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium">{card.title}</h3>
                        <p className="text-sm text-muted-foreground">{card.description}</p>
                      </div>
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Top Specialists */}
          <div>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Топ специалистов</h2>
              <Button variant="ghost" size="sm">
                Видеть всех
                <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </div>
            <div className="space-y-3">
              {topMasters.map((master) => (
                <Card key={master.id} className="transition-all hover:shadow-md">
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-3">
                      <div className="relative">
                        <Avatar className="h-12 w-12">
                          <AvatarImage src={master.avatar} alt={master.name} />
                          <AvatarFallback>{master.name.charAt(0)}</AvatarFallback>
                        </Avatar>
                        {master.is_online && (
                          <div className="absolute -bottom-1 -right-1 h-4 w-4 rounded-full bg-green-500 border-2 border-background" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h3 className="font-medium">{master.name}</h3>
                          <span className="text-sm text-muted-foreground">{master.profession}</span>
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                          <div className="flex items-center space-x-1">
                            <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                            <span>{master.rating}</span>
                            <span>({master.reviews_count} отзывов)</span>
                          </div>
                          <span>{master.hourly_rate}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button size="sm">Выбрать</Button>
                        <Button variant="ghost" size="sm">
                          <Heart className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Support Section */}
          <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <div className="rounded-full bg-blue-500 p-2">
                  <Users className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-medium">Алиса Онлайн техподдержка</h3>
                  <p className="text-sm text-muted-foreground">Поможем с любыми вопросами</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </Main>
    </>
  );
}

const clientTopNav = [
  {
    title: "Главная",
    href: "/dashboard/client",
    isActive: true,
    disabled: false,
  },
  {
    title: "Мастера",
    href: "/service-providers",
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
    href: "/orders",
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
