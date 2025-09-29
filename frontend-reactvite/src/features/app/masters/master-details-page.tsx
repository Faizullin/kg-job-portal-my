import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import myApi from "@/lib/api/my-api";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { Award, CheckCircle, Clock, Globe, GraduationCap, Heart, MoreVertical, Plus, ShoppingBag, Star } from "lucide-react";
import { useState } from "react";

interface MasterDetailsPageProps {
  providerId: string;
}

export function MasterDetailsPage({ providerId }: MasterDetailsPageProps) {
  const navigate = useNavigate();
  const [isFavorite, setIsFavorite] = useState(false);

  const { data: provider, isLoading, error } = useQuery({
    queryKey: ['service-provider-detail', providerId],
    queryFn: async () => {
      const response = await myApi.v1UsersMastersDetailsRetrieve({
        id: parseInt(providerId),
      });
      return response.data;
    },
    enabled: !!providerId,
  });

  const { data: reviews } = useQuery({
    queryKey: ['provider-reviews', providerId],
    queryFn: async () => {
      const response = await myApi.v1ReviewsProviderList({
        providerId: parseInt(providerId),
        pageSize: 10,
      });
      return response.data;
    },
    enabled: !!providerId,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка профиля мастера...</p>
        </div>
      </div>
    );
  }

  if (error || !provider) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Ошибка загрузки профиля мастера</p>
        </div>
      </div>
    );
  }

  const stats = [
    { label: "Заказов", value: provider.statistics?.total_jobs_completed || '~', color: "text-green-600" },
    { label: "Отзывов", value: provider.statistics?.total_reviews || '~', color: "text-green-600" },
    { label: "В срок", value: provider.statistics?.on_time_percentage ? `${provider.statistics.on_time_percentage}%` : '~', color: "text-blue-600" },
    { label: "Повторно", value: provider.statistics?.repeat_customer_percentage ? `${provider.statistics.repeat_customer_percentage}%` : '~', color: "text-purple-600" },
  ];

  const skills = provider.provider_skills?.map(skill => skill.skill?.name).filter(Boolean) || [];
  const workExamples = provider.portfolio_items?.slice(0, 2) || [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white px-4 py-3 flex items-center justify-between border-b">
        <h1 className="text-lg font-semibold">Профиль мастера</h1>
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsFavorite(!isFavorite)}
            className="p-2"
          >
            <Heart className={`h-5 w-5 ${isFavorite ? 'fill-red-500 text-red-500' : 'text-gray-400'}`} />
          </Button>
          <Button variant="ghost" size="sm" className="p-2">
            <MoreVertical className="h-5 w-5 text-gray-400" />
          </Button>
        </div>
      </div>

      <div className="px-4 py-6 space-y-6">
        {/* Master Info */}
        <div className="bg-white rounded-lg p-4">
          <div className="flex items-start space-x-4">
            <div className="relative">
              <Avatar className="h-16 w-16">
                <AvatarImage src={provider.user_profile?.user?.photo_url || "/images/avatar.png"} />
                <AvatarFallback className="text-lg">
                  {provider.user_profile?.user?.first_name?.[0] || provider.user_profile?.user?.username?.[0]}{provider.user_profile?.user?.last_name?.[0] || ''}
                </AvatarFallback>
              </Avatar>
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold text-gray-900">
                {provider.user_profile?.user?.first_name && provider.user_profile?.user?.last_name
                  ? `${provider.user_profile.user.first_name} ${provider.user_profile.user.last_name}`
                  : provider.user_profile?.user?.username || 'Мастер'}
              </h2>
              <p className="text-gray-600">{provider.profession?.name || "Мастер"}</p>
              <div className="flex items-center space-x-2 mt-2">
                {provider.user_profile.is_verified && (
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Проверен
                  </Badge>
                )}
                {provider.is_top_master && (
                  <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                    <Award className="h-3 w-3 mr-1" />
                    ТОП мастер
                  </Badge>
                )}
              </div>
            </div>
            <div className="flex flex-col space-y-2">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                <ShoppingBag className="h-4 w-4 mr-2" />
                Выбрать
              </Button>
              <Button variant="outline" className="border-yellow-400 text-yellow-600 hover:bg-yellow-50">
                <Plus className="h-4 w-4 mr-2" />
                ТОП мастер
              </Button>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="bg-white rounded-lg p-4">
          <div className="grid grid-cols-4 gap-4">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Work Examples */}
        {workExamples.length > 0 && (
          <div className="bg-white rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Примеры работ</h3>
            <div className="grid grid-cols-2 gap-4">
              {workExamples.map((item, index) => (
                <div key={index} className="aspect-square bg-gray-200 rounded-lg overflow-hidden">
                  <img
                    src={item.image || "/placeholder-work.jpg"}
                    alt={item.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              ))}
            </div>
            {workExamples.length > 2 && (
              <div className="flex justify-center mt-4 space-x-2">
                {Array.from({ length: Math.ceil(workExamples.length / 2) }).map((_, index) => (
                  <div
                    key={index}
                    className={`w-2 h-2 rounded-full ${index === 0 ? 'bg-blue-600' : 'bg-gray-300'}`}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Skills */}
        {skills.length > 0 && (
          <div className="bg-white rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Что умеет</h3>
            <div className="flex flex-wrap gap-2">
              {skills.map((skill, index) => (
                <Badge key={index} variant="outline" className="px-3 py-1">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Service Details */}
        <div className="bg-white rounded-lg p-4">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-gray-900">{provider.statistics?.total_jobs_completed || '~'}</div>
              <div className="text-sm text-gray-600">работ</div>
            </div>
            <div>
              <div className="text-lg font-bold text-gray-900">{provider.hourly_rate ? `${provider.hourly_rate} ₸` : '~'}</div>
              <div className="text-sm text-gray-600">за час</div>
            </div>
            <div>
              <div className="text-lg font-bold text-gray-900">{provider.response_time_hours || '~'}</div>
              <div className="text-sm text-gray-600">часа скорость ответа</div>
            </div>
          </div>
        </div>

        {/* Client Reviews */}
        {reviews?.results && reviews.results.length > 0 && (
          <div className="bg-white rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Отзывы клиентов</h3>
            <div className="space-y-4">
              {reviews.results.slice(0, 2).map((review) => (
                <div key={review.id} className="flex items-start space-x-3">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="text-sm">
                      {review.reviewer_name?.[0] || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium text-gray-900">{review.reviewer_name || '~'}</span>
                      <div className="flex items-center space-x-1">
                        {Array.from({ length: 5 }).map((_, starIndex) => (
                          <Star
                            key={starIndex}
                            className={`h-4 w-4 ${
                              starIndex < (review.overall_rating || 0)
                                ? 'text-yellow-400 fill-current'
                                : 'text-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {review.comment || '~'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            {reviews.results.length > 2 && (
              <div className="flex justify-center mt-4 space-x-2">
                {Array.from({ length: Math.ceil(reviews.results.length / 2) }).map((_, index) => (
                  <div
                    key={index}
                    className={`w-2 h-2 rounded-full ${index === 0 ? 'bg-blue-600' : 'bg-gray-300'}`}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* About Specialist */}
        {provider.about_description && (
          <div className="bg-white rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">О специалисте</h3>
            <p className="text-gray-600 leading-relaxed">{provider.about_description}</p>
          </div>
        )}

        {/* Professional Information */}
        <div className="bg-white rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Профессиональная информация</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <Clock className="h-4 w-4 text-gray-400" />
              <div>
                <span className="text-sm font-medium">Опыт работы:</span>
                <span className="text-sm text-gray-600 ml-2">
                  {provider.work_experience_start_year ? `С ${provider.work_experience_start_year} года` : "~"}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <GraduationCap className="h-4 w-4 text-gray-400" />
              <div>
                <span className="text-sm font-medium">Образование:</span>
                <span className="text-sm text-gray-600 ml-2">
                  {provider.education_institution || "~"}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Globe className="h-4 w-4 text-gray-400" />
              <div>
                <span className="text-sm font-medium">Языки:</span>
                <span className="text-sm text-gray-600 ml-2">
                  {Array.isArray(provider.languages) ? provider.languages.join(", ") : provider.languages || "~"}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Certificates */}
        {provider.certificates && provider.certificates.length > 0 && (
          <div className="bg-white rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Сертификаты</h3>
            <div className="flex flex-wrap gap-2">
              {provider.certificates.map((cert, index) => (
                <Badge key={index} variant="outline" className="px-3 py-1">
                  {cert.name || '~'}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Call to Action */}
        <div className="bg-blue-600 rounded-lg p-4 text-center">
          <Button 
            onClick={() => navigate({ to: '/app/jobs/create' })}
            className="w-full bg-white text-blue-600 hover:bg-gray-100 text-lg font-semibold py-3"
          >
            Рассказать о задаче
          </Button>
        </div>
      </div>
    </div>
  );
}
