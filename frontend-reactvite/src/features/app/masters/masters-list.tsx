import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { TopNav } from "@/components/layout/top-nav";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { ThemeSwitch } from "@/components/theme-switch";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useDebounce } from "@/hooks/use-debounce";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  Bell,
  Clock,
  Heart,
  MapPin,
  MessageCircle,
  Search as SearchIcon,
  Star,
  Users,
  Eye,
  ShoppingCart
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Link } from "@tanstack/react-router";

const MASTERS_LIST_QUERY_KEY = 'masters-list';
const CATEGORIES_QUERY_KEY = 'categories';

export function MastersList() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [favoriteMasters, setFavoriteMasters] = useState<Set<number>>(new Set());
  const debouncedSearch = useDebounce(searchQuery, 300);
  const queryClient = useQueryClient();

  // Fetch masters list from backend
  const { data: mastersData, isLoading, error } = useQuery({
    queryKey: [MASTERS_LIST_QUERY_KEY, debouncedSearch, selectedCategory],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (debouncedSearch) {
        params.append('search', debouncedSearch);
      }
      if (selectedCategory) {
        params.append('services_offered__category', selectedCategory.toString());
      }
      // Add default filters for better results
      params.append('is_available', 'true');
      params.append('ordering', '-statistics__average_rating');
      
      const response = await myApi.axios.get(`/api/v1/search/providers/?${params.toString()}`);
      return response.data;
    },
    retry: 2,
  });

  // Handle error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-red-600">Ошибка загрузки</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Не удалось загрузить список мастеров
          </p>
          <Button 
            onClick={() => queryClient.invalidateQueries({ queryKey: [MASTERS_LIST_QUERY_KEY] })}
            className="mt-4"
          >
            Попробовать снова
          </Button>
        </div>
      </div>
    );
  }

  // Fetch categories for filtering
  const { data: categoriesData } = useQuery({
    queryKey: [CATEGORIES_QUERY_KEY],
    queryFn: async () => {
      const response = await myApi.axios.get('/api/v1/core/service-categories/');
      return response.data;
    },
    retry: 2,
  });

  const masters = mastersData?.results || [];
  const categories = categoriesData?.results || [];

  // Favorite master mutation
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

  const handleFavoriteMaster = (masterId: number) => {
    favoriteMutation.mutate(masterId);
  };

  const topNavLinks = [
    { title: "Главная", href: "/app/client", isActive: false },
    { title: "Мастера", href: "/app/masters", isActive: true },
    { title: "Сообщения", href: "/messages", isActive: false },
    { title: "Заказы", href: "/orders", isActive: false },
    { title: "Профиль", href: "/profile", isActive: false },
  ];

  return (
    <>
      <Header>
        <TopNav links={topNavLinks} />
        <div className="ms-auto flex items-center space-x-4">
          <Button variant="ghost" size="sm" className="relative">
            <Bell className="h-4 w-4" />
            <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-red-500 text-xs text-white flex items-center justify-center">
              3
            </span>
          </Button>
          <ThemeSwitch />
          <ProfileDropdown />
        </div>
      </Header>

      <Main>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" asChild>
                <Link to="/app/client">
                  <ArrowLeft className="h-4 w-4" />
                </Link>
              </Button>
              <div>
                <h1 className="text-2xl font-bold">Выберите мастера</h1>
                <p className="text-muted-foreground">
                  Найдено {masters.length} мастеров
                </p>
              </div>
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Найти мастера (например: мебель, перевод)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Service Categories */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-muted-foreground">Категории услуг</h3>
            <div className="flex space-x-3 overflow-x-auto pb-2">
              <Button
                variant={selectedCategory === null ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(null)}
                className="whitespace-nowrap"
              >
                Все
              </Button>
              {categories.map((category: any) => (
                <Button
                  key={category.id}
                  variant={selectedCategory === category.id ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedCategory(category.id)}
                  className="whitespace-nowrap"
                >
                  {category.name}
                </Button>
              ))}
            </div>
          </div>

          {/* Masters List */}
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
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
              {masters.map((master: any) => (
                <Card key={master.id} className="transition-all hover:shadow-lg group">
                  <CardContent className="p-6">
                    <div className="flex items-start space-x-4">
                      {/* Avatar */}
                      <div className="relative">
                        <Avatar className="h-16 w-16">
                          <AvatarImage 
                            src={master.photo_url} 
                            alt={`${master.first_name} ${master.last_name}`} 
                          />
                          <AvatarFallback className="bg-blue-100 text-blue-600 text-lg">
                            {master.first_name?.charAt(0) || master.username?.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        {master.service_provider_profile?.is_online && (
                          <div className="absolute -bottom-1 -right-1 h-5 w-5 rounded-full bg-green-500 border-2 border-background">
                            <div className="absolute inset-0 rounded-full bg-green-400 animate-pulse" />
                          </div>
                        )}
                      </div>

                      {/* Master Info */}
                      <div className="flex-1 space-y-3">
                        {/* Name and Profession */}
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="text-lg font-semibold">
                              {master.first_name && master.last_name 
                                ? `${master.first_name} ${master.last_name}` 
                                : master.username}
                            </h3>
                            <p className="text-muted-foreground">
                              {master.service_provider_profile?.profession?.name || 'Специалист'}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            {master.service_provider_profile?.is_top_master && (
                              <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                                <Star className="h-3 w-3 mr-1" />
                                ТОП мастер
                              </Badge>
                            )}
                            {master.service_provider_profile?.is_verified_provider && (
                              <Badge variant="secondary" className="bg-green-100 text-green-800">
                                ✓ Проверен
                              </Badge>
                            )}
                          </div>
                        </div>

                        {/* Rating and Reviews */}
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center space-x-1">
                            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                            <span className="font-semibold">
                              {master.service_provider_profile?.statistics?.average_rating || 0}
                            </span>
                            <span className="text-muted-foreground">
                              ({master.service_provider_profile?.statistics?.total_reviews || 0} отзывов)
                            </span>
                          </div>
                          <div className="flex items-center space-x-1 text-muted-foreground">
                            <Users className="h-4 w-4" />
                            <span>
                              {master.service_provider_profile?.statistics?.total_jobs_completed || 0} работ
                            </span>
                          </div>
                        </div>

                        {/* Work Examples */}
                        <div className="space-y-2">
                          <h4 className="text-sm font-medium text-muted-foreground">Примеры работ</h4>
                          <div className="flex space-x-2">
                            {[...Array(3)].map((_, i) => (
                              <div key={i} className="h-16 w-16 bg-gray-100 rounded-lg flex items-center justify-center">
                                <span className="text-xs text-muted-foreground">Фото {i + 1}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Skills */}
                        <div className="space-y-2">
                          <h4 className="text-sm font-medium text-muted-foreground">Что умеет</h4>
                          <div className="flex flex-wrap gap-2">
                            <Badge variant="outline">Сборка мебели</Badge>
                            <Badge variant="outline">Установка полок</Badge>
                            <Badge variant="outline">+1</Badge>
                          </div>
                        </div>

                        {/* Stats and Location */}
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-1">
                              <Clock className="h-4 w-4 text-muted-foreground" />
                              <span>
                                Отвечает за {master.service_provider_profile?.response_time_hours || 24} часа
                              </span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <MapPin className="h-4 w-4 text-muted-foreground" />
                              <span>
                                {master.service_provider_profile?.current_location || 'Бишкек'}
                              </span>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold text-green-600">
                              {master.service_provider_profile?.hourly_rate 
                                ? `${master.service_provider_profile.hourly_rate}₸/час`
                                : "Цена договорная"}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex flex-col space-y-2">
                        <Button size="sm" variant="outline" className="w-full">
                          <Eye className="h-4 w-4 mr-2" />
                          Посмотреть
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
                          {favoriteMasters.has(master.id) ? "В избранном" : "В избранное"}
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
