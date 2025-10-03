import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChatTypeEnum } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { ArrowLeft, Award, CheckCircle, Clock, Eye, Globe, GraduationCap, Heart, MessageCircle, ShoppingBag, Star, Users } from "lucide-react";
import { useCallback, useMemo, useState } from "react";

interface MasterDetailsPageProps {
  masterId: string;
}

export function MasterDetailsPage({ masterId }: MasterDetailsPageProps) {
  const navigate = useNavigate();
  const [isFavorite, setIsFavorite] = useState(false);

  const loadMasterDetailsQuery = useQuery({
    queryKey: ['master-details', masterId],
    queryFn: async () => {
      const response = await myApi.v1UsersMastersDetails({
        id: parseInt(masterId),
      });
      return response.data;
    },
    enabled: !!masterId,
  });

  const loadMasterReviewsQuery = useQuery({
    queryKey: ['master-reviews', masterId],
    queryFn: async () => {
      const response = await myApi.v1ReviewsMasterList({
        masterId: parseInt(masterId),
        pageSize: 10,
      });
      return response.data;
    },
    enabled: !!masterId,
  });
  const master = loadMasterDetailsQuery.data;
  const reviews = loadMasterReviewsQuery.data;

  const handleFavoriteToggle = useCallback(() => {
    setIsFavorite(!isFavorite);
  }, [isFavorite]);

  // Find or create chat room with master
  const findOrCreateChatMutation = useMutation({
    mutationFn: async () => {
      const roomsResponse = await myApi.v1ChatsRoomsForMaster({
        masterId: parseInt(masterId),
      });
      if (roomsResponse.data.length > 0) {
        return roomsResponse.data[0];
      }

      const response = await myApi.v1ChatsRoomsCreate({
        chatRoomCreateRequest: {
          title: `Чат с ${master?.user?.first_name && master?.user?.last_name
            ? `${master.user.first_name} ${master.user.last_name}`
            : master?.user?.username || "Мастер"}`,
          chat_type: ChatTypeEnum.job_chat,
          participants_users_ids: [parseInt(masterId)],
        } as any
      });
      return response.data;
    },
    onSuccess: (chatRoom) => {
      // Navigate to the chat room using search params
      navigate({ to: '/chats', search: { chat_room_id: chatRoom.id } });
    },
    onError: (error) => {
      console.error("Error finding or creating chat:", error);
    }
  });

  const handleOpenChat = useCallback(() => {
    findOrCreateChatMutation.mutate();
  }, [findOrCreateChatMutation]);



  const skills = useMemo(() =>
    master?.skills?.map((skill) => skill.skill?.name).filter(Boolean) || [],
    [master?.skills]
  );

  const workExamples = useMemo(() =>
    master?.portfolio_items?.slice(0, 2) || [],
    [master?.portfolio_items]
  );

  if (loadMasterDetailsQuery.isLoading || !master) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка профиля мастера...</p>
        </div>
      </div>
    );
  }

  if (loadMasterDetailsQuery.error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Ошибка загрузки профиля мастера</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Blue Header with Statistics */}
      <div className="bg-blue-600 text-white px-4 py-6">
        <div className="flex items-center mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate({ to: '/app/masters' })}
            className="text-white hover:bg-blue-700 p-2 mr-3"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-xl font-bold">Профиль мастера</h1>
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-green-400">{master?.statistics?.total_jobs_completed}</div>
            <div className="text-sm text-blue-100">Заказов</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-400">{master?.statistics?.total_reviews}</div>
            <div className="text-sm text-blue-100">Отзывов</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-300">{master?.statistics?.on_time_percentage}%</div>
            <div className="text-sm text-blue-100">В срок</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-300">{master?.statistics?.repeat_customer_percentage}%</div>
            <div className="text-sm text-blue-100">Повторно</div>
          </div>
        </div>
      </div>

      <div className="px-4 py-6 space-y-6">
        {/* Master Profile Card */}
        <div className="bg-white rounded-lg p-6">
          <div className="flex items-start space-x-4">
            <div className="relative">
              <Avatar className="h-20 w-20">
                <AvatarImage src={master.user?.photo_url || undefined} />
                <AvatarFallback className="text-xl">
                  {master.user?.first_name?.[0] || master.user?.username?.[0]}{master.user?.last_name?.[0] || ''}
                </AvatarFallback>
              </Avatar>
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 mb-1">
                {master.user?.first_name && master.user?.last_name
                  ? `${master.user.first_name} ${master.user.last_name}`
                  : master.user?.username}
              </h2>
              <p className="text-gray-600 mb-3">{master.profession?.name}</p>

              {/* Rating and Reviews */}
              <div className="flex items-center space-x-2 mb-3">
                <div className="flex items-center space-x-1">
                  {Array.from({ length: 5 }).map((_, starIndex) => (
                    <Star
                      key={starIndex}
                      className={`h-4 w-4 ${starIndex < 4 ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                    />
                  ))}
                </div>
                <span className="font-semibold text-gray-900">
                  {master?.statistics?.average_rating}
                </span>
                <span className="text-gray-600">
                  ({master?.statistics?.total_reviews} отзывов)
                </span>
              </div>

              {/* Badges */}
              <div className="flex items-center space-x-2 mb-4">
                {master.is_verified_provider && (
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Проверен
                  </Badge>
                )}
                {master.is_top_master && (
                  <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                    <Award className="h-3 w-3 mr-1" />
                    ТОП мастер
                  </Badge>
                )}
              </div>

              {/* Work Examples */}
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Примеры работ</h3>
                <div className="grid grid-cols-2 gap-2">
                  {workExamples.map((item, index) => (
                    <div key={index} className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                      {
                        item.attachments.length > 0 ? (
                          <>
                            <img
                              src={item.attachments[0]!.file_url || undefined}
                              alt={item.title}
                              className="w-full h-full object-cover"
                            />
                          </>
                        ) : null
                      }
                    </div>
                  ))}
                </div>
              </div>

              {/* Skills */}
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Что умеет</h3>
                <div className="flex flex-wrap gap-2">
                  {skills.map((skill, index) => (
                    <Badge key={index} variant="outline" className="px-3 py-1">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Detailed Stats */}
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-1">
                    <Users className="h-4 w-4 text-gray-400" />
                    <span>{master?.statistics?.total_jobs_completed} работ</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Clock className="h-4 w-4 text-gray-400" />
                    <span>{master?.response_time_hours} часа скорость ответа</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-green-600">
                    {master?.hourly_rate}₸/час
                  </div>
                  {master?.is_online && (
                    <div className="flex items-center space-x-1 text-green-600 text-xs">
                      <div className="h-2 w-2 rounded-full bg-green-500" />
                      <span>Сейчас онлайн</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col space-y-2">
              <Button variant="outline" size="sm" className="w-full">
                <Eye className="h-4 w-4 mr-2" />
                Посмотреть
              </Button>
              <Button className="bg-blue-600 hover:bg-blue-700 text-white w-full">
                <ShoppingBag className="h-4 w-4 mr-2" />
                Выбрать
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleFavoriteToggle}
                className={`w-full ${isFavorite ? 'text-red-500' : 'text-gray-400'}`}
              >
                <Heart className={`h-4 w-4 ${isFavorite ? 'fill-current' : ''}`} />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="w-full"
                onClick={handleOpenChat}
                disabled={findOrCreateChatMutation.isPending}
              >
                <MessageCircle className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>



        {/* Client Reviews */}
        {reviews?.results && reviews.results.length > 0 && (
          <div className="bg-white rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Отзывы клиентов</h3>
            <div className="space-y-4">
              {reviews.results.slice(0, 2).map((review) => (
                <div key={review.id} className="flex items-start space-x-3">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="text-sm">
                      {review.reviewer?.first_name?.[0] || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-medium text-gray-900">
                        {review.reviewer?.first_name} {review.reviewer?.last_name}
                      </span>
                      <div className="flex items-center space-x-1">
                        {Array.from({ length: 5 }).map((_, starIndex) => (
                          <Star
                            key={starIndex}
                            className={`h-4 w-4 ${starIndex < (review.rating || 0)
                              ? 'text-yellow-400 fill-current'
                              : 'text-gray-300'
                              }`}
                          />
                        ))}
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {review.comment}
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

        {master.about_description && (
          <div className="bg-white rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">О специалисте</h3>
            <p className="text-gray-600 leading-relaxed">{master.about_description}</p>
          </div>
        )}

        {/* Professional Information */}
        <div className="bg-white rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Профессиональная информация</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <Clock className="h-5 w-5 text-gray-400" />
              <div>
                <span className="text-sm font-medium">Опыт работы:</span>
                <span className="text-sm text-gray-600 ml-2">
                  {master.work_experience_start_year ? `С ${master.work_experience_start_year} года` : undefined}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <GraduationCap className="h-5 w-5 text-gray-400" />
              <div>
                <span className="text-sm font-medium">Образование:</span>
                <span className="text-sm text-gray-600 ml-2">
                  {master.education_institution}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Globe className="h-5 w-5 text-gray-400" />
              <div>
                <span className="text-sm font-medium">Языки:</span>
                <span className="text-sm text-gray-600 ml-2">
                  {Array.isArray(master.languages) ? master.languages.join(", ") : master.languages}
                </span>
              </div>
            </div>
          </div>
        </div>

        {master.certificates && master.certificates.length > 0 && (
          <div className="bg-white rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Сертификаты</h3>
            <div className="flex flex-wrap gap-2">
              {master.certificates.map((cert, index) => (
                <Badge key={index} variant="outline" className="px-3 py-1">
                  {cert.name}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Call to Action */}
        <div className="space-y-3">
          <div className="bg-green-600 rounded-lg p-6 text-center">
            <Button
              onClick={handleOpenChat}
              disabled={findOrCreateChatMutation.isPending}
              className="w-full bg-white text-green-600 hover:bg-gray-100 text-lg font-semibold py-4"
            >
              <MessageCircle className="h-5 w-5 mr-2" />
              {findOrCreateChatMutation.isPending ? "Открытие чата..." : "Написать мастеру"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
