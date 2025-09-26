import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useDebounce } from "@/hooks/use-debounce";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import {
  Eye,
  Heart,
  MapPin,
  Search as SearchIcon,
  Star
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

const SERVICE_PROVIDERS_QUERY_KEY = 'service-providers';

export function ServiceProvidersList() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [favoriteProviders, setFavoriteProviders] = useState<Set<number>>(new Set());
  const debouncedSearch = useDebounce(searchQuery, 300);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  // Fetch service providers from backend
  const { data: providersData, isLoading, error } = useQuery({
    queryKey: [SERVICE_PROVIDERS_QUERY_KEY, debouncedSearch, selectedCategory],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (debouncedSearch) {
        params.append('search', debouncedSearch);
      }
      if (selectedCategory) {
        params.append('job_portal_profile__service_provider_profile__services_offered__category', selectedCategory.toString());
      }

      const response = await myApi.v1SearchProvidersList({
        search: debouncedSearch,
      });
      return response.data;
    },
    retry: 2,
  });

  // Fetch categories for filtering
  const { data: categoriesData } = useQuery({
    queryKey: ['service-categories'],
    queryFn: async () => {
      const response = await myApi.v1CoreServiceCategoriesList();
      return response.data;
    },
    retry: 2,
  });

  const providers = providersData?.results || [];
  const categories = categoriesData?.results || [];

  // Favorite mutation
  const favoriteMutation = useMutation({
    mutationFn: async (providerId: number) => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return providerId;
    },
    onSuccess: (providerId) => {
      setFavoriteProviders(prev => {
        const newSet = new Set(prev);
        if (newSet.has(providerId)) {
          newSet.delete(providerId);
          toast.success("Удалено из избранного");
        } else {
          newSet.add(providerId);
          toast.success("Добавлено в избранное");
        }
        return newSet;
      });
    },
    onError: () => {
      toast.error("Ошибка при обновлении избранного");
    }
  });

  const handleFavoriteProvider = (providerId: number) => {
    favoriteMutation.mutate(providerId);
  };


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
            onClick={() => queryClient.invalidateQueries({ queryKey: [SERVICE_PROVIDERS_QUERY_KEY] })}
            className="mt-4"
          >
            Попробовать снова
          </Button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
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
    );
  }

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Найти мастера (например: мебель, перевод)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>{providersData?.count} мастеров</span>
        <span>4.8 средняя оценка</span>
        <span>24 время ответа</span>
      </div>

      {/* Service Categories */}
      <div>
        <h3 className="mb-3 text-sm font-medium">Категории услуг</h3>
        <div className="flex space-x-3 overflow-x-auto pb-2">
          <Button
            variant={selectedCategory === null ? "default" : "outline"}
            size="sm"
            onClick={() => setSelectedCategory(null)}
            className="whitespace-nowrap flex-shrink-0"
          >
            Все
          </Button>
          {categories.map((category) => (
            <Button
              key={category.id}
              variant={selectedCategory === category.id ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(category.id)}
              className="whitespace-nowrap flex-shrink-0"
            >
              {category.name}
            </Button>
          ))}
        </div>
      </div>

      {/* Service Providers */}
      <div className="space-y-4">
        {providers?.map((provider) => (
          <Card key={provider.id} className="transition-all hover:shadow-md">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <div className="relative">
                  <Avatar className="h-16 w-16">
                    <AvatarImage src={provider.photo_url || "/images/avatar.png"} alt={`${provider.first_name} ${provider.last_name}`} />
                    <AvatarFallback className="bg-blue-100 text-blue-600 text-lg">
                      {provider.first_name?.charAt(0) || provider.username?.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  {provider.job_portal_profile?.service_provider_profile?.is_online && (
                    <div className="absolute -bottom-1 -right-1 h-4 w-4 rounded-full bg-green-500 border-2 border-background">
                      <div className="absolute inset-0 rounded-full bg-green-400 animate-pulse" />
                    </div>
                  )}
                </div>

                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-lg">
                        {provider.first_name && provider.last_name
                          ? `${provider.first_name} ${provider.last_name}`
                          : provider.username}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {provider.job_portal_profile?.service_provider_profile.profession.name}
                      </p>
                    </div>
                    {provider.job_portal_profile?.service_provider_profile?.is_top_master && (
                      <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                        ТОП мастер
                      </Badge>
                    )}
                  </div>

                  <div className="flex items-center space-x-1">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span className="font-medium">
                      {provider.job_portal_profile?.service_provider_profile?.statistics?.average_rating}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      ({provider.job_portal_profile?.service_provider_profile?.statistics?.total_reviews } отзывов)
                    </span>
                  </div>

                  {/* Work Examples */}
                  <div>
                    <p className="text-sm font-medium mb-1">Примеры работ</p>
                    <div className="flex space-x-2">
                      {provider.job_portal_profile?.service_provider_profile?.portfolio_items?.slice(0, 3).map((item, index) => (
                        <div key={index} className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center overflow-hidden">
                          {item.image ? (
                            <img 
                              src={item.image} 
                              alt={item.title} 
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-8 h-8 bg-yellow-300 rounded"></div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Skills */}
                  <div>
                    <p className="text-sm font-medium mb-1">Что умеет</p>
                    <div className="flex flex-wrap gap-1">
                      {provider.job_portal_profile?.service_provider_profile?.provider_skills?.slice(0, 3).map((skill, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {skill.skill.name}
                        </Badge>
                      ))}
                      {provider.job_portal_profile?.service_provider_profile?.provider_skills?.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{provider.job_portal_profile.service_provider_profile.provider_skills.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Statistics */}
                  <div className="flex items-center justify-between text-sm">
                    <span>{provider.job_portal_profile?.service_provider_profile?.statistics?.total_jobs_completed} работ</span>
                    <span className="font-medium text-green-600">
                      {provider.job_portal_profile?.service_provider_profile?.hourly_rate
                        ? `${provider.job_portal_profile.service_provider_profile.hourly_rate}₸/час`
                        : "Цена договорная"}
                    </span>
                    <span>Отвечает за {provider.job_portal_profile?.service_provider_profile?.response_time_hours || 24} часа</span>
                  </div>

                  {/* Location */}
                  <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                    <MapPin className="h-3 w-3" />
                    <span>{provider.job_portal_profile?.service_provider_profile?.current_location}</span>
                    <div className="flex items-center space-x-1 ml-auto">
                      <div className="h-2 w-2 rounded-full bg-green-500"></div>
                      <span className="text-xs">Сейчас онлайн</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-2 pt-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => navigate({ to: "/app/service-providers/$providerId", params: { providerId: provider.job_portal_profile?.service_provider_profile?.id?.toString() || provider.id.toString() } })}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      Посмотреть
                    </Button>
                    <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                      Выбрать
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleFavoriteProvider(provider.id)}
                      className={favoriteProviders.has(provider.id) ? "text-red-500" : "text-muted-foreground"}
                    >
                      <Heart className={`h-4 w-4 ${favoriteProviders.has(provider.id) ? "fill-current" : ""}`} />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

