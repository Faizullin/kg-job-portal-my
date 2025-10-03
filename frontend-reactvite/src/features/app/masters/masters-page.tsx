import { ConfigDrawer } from "@/components/config-drawer";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { TopNav } from "@/components/layout/top-nav";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { ThemeSwitch } from "@/components/theme-switch";
import { NotificationsDropdown } from "@/components/notifications/notifications-dropdown";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useDebounce } from "@/hooks/use-debounce";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { PaginatedMasterSearchList, PaginatedServiceCategoryList } from "@/lib/api/axios-client/api";
import { Link } from "@tanstack/react-router";
import {
  ArrowLeft,
  Clock,
  Heart,
  MapPin,
  MessageCircle,
  Search as SearchIcon,
  Star,
  Users,
  Eye,
  ShoppingCart,
  CheckCircle,
  Wrench,
  Zap,
  Home,
  Settings
} from "lucide-react";
import { useState, useMemo, useCallback } from "react";
import { toast } from "sonner";

const MASTERS_PAGE_QUERY_KEY = 'masters-page';
const CATEGORIES_QUERY_KEY = 'categories';

export function MastersPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory] = useState<number | null>(null);
  const [favoriteMasters, setFavoriteMasters] = useState<Set<number>>(new Set());
  const debouncedSearch = useDebounce(searchQuery, 300);
  const queryClient = useQueryClient();

  const loadSearchMastersListQuery = useQuery<PaginatedMasterSearchList>({
    queryKey: [MASTERS_PAGE_QUERY_KEY, debouncedSearch, selectedCategory],
    queryFn: () => myApi.v1SearchMastersList({
      isAvailable: true,
      ordering: '-statistics__average_rating',
      pageSize: 20,
      search: debouncedSearch || undefined,
      servicesOfferedCategory: selectedCategory || undefined,
    }).then(response => response.data),
    retry: 2,
  });

  const loadServiceCategoriesQuery = useQuery<PaginatedServiceCategoryList>({
    queryKey: [CATEGORIES_QUERY_KEY],
    queryFn: () => myApi.v1CoreServiceCategoriesList({
      isActive: true,
      featured: true,
      pageSize: 10,
    }).then(response => response.data),
    retry: 2,
  });

  const masters = useMemo(() => {
    return loadSearchMastersListQuery.data?.results || [];
  }, [loadSearchMastersListQuery.data])
  const categories = loadServiceCategoriesQuery.data?.results || [];

  const stats = useMemo(() => ({
    totalMasters: masters.length,
    averageRating: masters.length > 0 
      ? (masters.reduce((sum: number, master) => 
          sum + (parseFloat(master.statistics?.average_rating || '0')), 0) / masters.length
        ).toFixed(1)
      : '0.0',
    averageResponseTime: masters.length > 0
      ? Math.round(masters.reduce((sum: number, master) => 
          sum + (master.response_time_hours || 0), 0) / masters.length
        )
      : 0
  }), [masters]);

  const favoriteMutation = useMutation({
    mutationFn: async (masterId: number) => {
      await new Promise(resolve => setTimeout(resolve, 500));
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

  const handleFavoriteMaster = useCallback((masterId: number) => {
    favoriteMutation.mutate(masterId);
  }, [favoriteMutation]);

  const iconMap = {
    'wrench': Wrench,
    'home': Home,
    'zap': Zap,
    'settings': Settings,
    'default': Settings,
  };

  const getIcon = (iconName: string) => {
    return iconMap[iconName as keyof typeof iconMap] || iconMap.default;
  };

  const topNavLinks = [
    { title: "Главная", href: "/app/client", isActive: false },
    { title: "Мастера", href: "/app/masters", isActive: true },
    { title: "Сообщения", href: "/chats", isActive: false },
    { title: "Заказы", href: "/jobs", isActive: false },
    { title: "Профиль", href: "/settings/profile", isActive: false },
  ];

  if (loadSearchMastersListQuery.error) {
    return (
      <>
        <Header>
          <TopNav links={topNavLinks} />
          <div className="ms-auto flex items-center space-x-4">
            <NotificationsDropdown />
            <ThemeSwitch />
            <ConfigDrawer />
            <ProfileDropdown />
          </div>
        </Header>
        <Main>
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-red-600">Ошибка загрузки</h3>
              <p className="text-sm text-muted-foreground mt-2">
                Не удалось загрузить список мастеров
              </p>
              <Button 
                onClick={() => queryClient.invalidateQueries({ queryKey: [MASTERS_PAGE_QUERY_KEY] })}
                className="mt-4"
              >
                Попробовать снова
              </Button>
            </div>
          </div>
        </Main>
      </>
    );
  }

  return (
    <>
      <Header>
        <TopNav links={topNavLinks} />
        <div className="ms-auto flex items-center space-x-4">
          <NotificationsDropdown />
          <ThemeSwitch />
          <ConfigDrawer />
          <ProfileDropdown />
        </div>
      </Header>

      <Main>
        <div className="space-y-6">
          <div className="bg-blue-600 text-white p-6 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <Button variant="ghost" size="sm" asChild className="text-white hover:bg-blue-700">
                  <Link to="/app/client">
                    <ArrowLeft className="h-4 w-4" />
                  </Link>
                </Button>
                <div>
                  <h1 className="text-xl font-bold">Выберите мастера</h1>
                  <p className="text-blue-100">
                    Найдено {stats.totalMasters} мастеров
                  </p>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold">{stats.totalMasters}</div>
                <div className="text-sm text-blue-100">мастеров</div>
              </div>
              <div>
                <div className="text-2xl font-bold">{stats.averageRating}</div>
                <div className="text-sm text-blue-100">средняя оценка</div>
              </div>
              <div>
                <div className="text-2xl font-bold">{stats.averageResponseTime}ч</div>
                <div className="text-sm text-blue-100">время ответа</div>
              </div>
            </div>
          </div>

          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Найти мастера (например: мебель, перевод)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <div>
            <div className="flex space-x-3 overflow-x-auto pb-2">
              {categories.slice(0, 5).map((category: any) => {
                const IconComponent = getIcon(category.icon || 'default');
                return (
                  <Card key={category.id} className="cursor-pointer hover:shadow-md transition-shadow min-w-[120px]">
                    <CardContent className="p-4">
                      <div className="text-center">
                        <div className="h-12 w-12 mx-auto mb-2 bg-primary/10 rounded-full flex items-center justify-center">
                          <IconComponent className="h-6 w-6 text-primary" />
                        </div>
                        <h3 className="font-medium text-sm">{category.name}</h3>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {loadSearchMastersListQuery.isLoading ? (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      <div className="h-16 w-16 bg-gray-200 rounded-full" />
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-gray-200 rounded w-1/3" />
                        <div className="h-3 bg-gray-200 rounded w-1/4" />
                        <div className="h-3 bg-gray-200 rounded w-1/2" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {masters.map((master) => (
                <Card key={master.id} className="transition-all hover:shadow-lg">
                  <CardContent className="p-6">
                    <div className="flex items-start space-x-4">
                      <div className="relative">
                        <Avatar className="h-16 w-16">
                          <AvatarImage 
                            src={master.user?.photo_url || undefined} 
                            alt={`${master.user?.first_name} ${master.user?.last_name}`} 
                          />
                          <AvatarFallback className="bg-blue-100 text-blue-600 text-lg">
                            {master.user?.first_name?.charAt(0) || master.user?.username?.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        {master.is_online && (
                          <div className="absolute -bottom-1 -right-1 h-5 w-5 rounded-full bg-green-500 border-2 border-background">
                            <div className="absolute inset-0 rounded-full bg-green-400 animate-pulse" />
                          </div>
                        )}
                      </div>

                      <div className="flex-1 space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="text-lg font-semibold">
                              {master.user?.first_name && master.user?.last_name 
                                ? `${master.user.first_name} ${master.user.last_name}` 
                                : master.user?.username}
                            </h3>
                            <p className="text-muted-foreground">
                              {master.profession?.name || 'Специалист'}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            {master.is_top_master && (
                              <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                                <Star className="h-3 w-3 mr-1" />
                                ТОП мастер
                              </Badge>
                            )}
                            {master.is_verified_provider && (
                              <Badge variant="secondary" className="bg-green-100 text-green-800">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Проверен
                              </Badge>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center space-x-4">
                          <div className="flex items-center space-x-1">
                            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                            <span className="font-semibold">
                              {master.statistics?.average_rating}
                            </span>
                            <span className="text-muted-foreground">
                              ({master.statistics?.total_reviews} отзывов)
                            </span>
                          </div>
                        </div>

                        {master.portfolio_items && master.portfolio_items.length > 0 && (
                          <div className="space-y-2">
                            <h4 className="text-sm font-medium text-muted-foreground">Примеры работ</h4>
                            <div className="flex space-x-2">
                              {master.portfolio_items.slice(0, 3).map((_, index) => (
                                <div key={index} className="h-16 w-16 bg-gray-100 rounded-lg flex items-center justify-center">
                                  <span className="text-xs text-muted-foreground">Фото {index + 1}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="space-y-2">
                          <h4 className="text-sm font-medium text-muted-foreground">Что умеет</h4>
                          <div className="flex flex-wrap gap-2">
                            {master.master_skills?.slice(0, 2).map((skill, index) => (
                              <Badge key={index} variant="outline">{skill.skill?.name}</Badge>
                            ))}
                            {master.master_skills?.length > 2 && (
                              <Badge variant="outline">+{master.master_skills.length - 2}</Badge>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-1">
                              <Users className="h-4 w-4 text-muted-foreground" />
                              <span>
                                {master.statistics?.total_jobs_completed} работ
                              </span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Clock className="h-4 w-4 text-muted-foreground" />
                              <span>
                                Отвечает за {master.response_time_hours} часа
                              </span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <MapPin className="h-4 w-4 text-muted-foreground" />
                              <span>
                                {master.current_location}
                              </span>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold text-green-600">
                              {master.hourly_rate}₸/час
                            </div>
                            {master.is_online && (
                              <div className="flex items-center space-x-1 text-green-600 text-xs">
                                <div className="h-2 w-2 rounded-full bg-green-500" />
                                <span>Сейчас онлайн</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-col space-y-2">
                        <Button size="sm" variant="outline" asChild className="w-full">
                          <Link to="/app/masters/$masterId" params={{ masterId: master.id.toString() }}>
                            <Eye className="h-4 w-4 mr-2" />
                            Посмотреть
                          </Link>
                        </Button>
                        <Button size="sm" className="w-full bg-blue-600 hover:bg-blue-700">
                          <ShoppingCart className="h-4 w-4 mr-2" />
                          Выбрать
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleFavoriteMaster(master.id)}
                          className={`w-full ${
                            favoriteMasters.has(master.id) ? "text-red-500" : "text-muted-foreground"
                          }`}
                        >
                          <Heart className={`h-4 w-4 ${favoriteMasters.has(master.id) ? "fill-current" : ""}`} />
                        </Button>
                        <Button variant="ghost" size="sm" className="w-full">
                          <MessageCircle className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </Main>
    </>
  );
}
