import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { TopNav } from "@/components/layout/top-nav";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { ThemeSwitch } from "@/components/theme-switch";
import { ConfigDrawer } from "@/components/config-drawer";
import myApi from "@/lib/api/my-api";
import { useQuery } from "@tanstack/react-query";
import { 
  Heart,
  MoreHorizontal,
  Star,
  Briefcase,
  GraduationCap,
  Globe,
  Award
} from "lucide-react";

interface ProviderDashboardData {
  provider_info?: {
    name: string;
    profession: string;
    is_top_master: boolean;
    is_verified: boolean;
    avatar?: string;
    location: string;
    is_online: boolean;
  };
  statistics?: {
    total_orders: number;
    total_reviews: number;
    on_time_percentage: number;
    repeat_customer_percentage: number;
    completed_jobs: number;
    hourly_rate: string;
    response_time: string;
  };
  portfolio?: Array<{
    id: number;
    title: string;
    description: string;
    image_url: string;
    created_at: string;
  }>;
  recent_reviews?: Array<{
    id: number;
    client_name: string;
    rating: number;
    comment: string;
    created_at: string;
    client_avatar?: string;
  }>;
  skills?: Array<{
    id: number;
    name: string;
    description: string;
  }>;
  certificates?: Array<{
    id: number;
    name: string;
    issuer: string;
    issue_date: string;
  }>;
  professional_info?: {
    work_experience: string;
    education: string;
    education_years: string;
    languages: string[];
    about: string;
  };
}

export function MasterDashboard() {
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboard', 'provider'],
    queryFn: async () => {
      const response = await myApi.axios.get('/api/v1/dashboard/provider/');
      return response.data as ProviderDashboardData;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const masterStats = dashboardData?.statistics || {
    total_orders: 0,
    total_reviews: 0,
    on_time_percentage: 0,
    repeat_customer_percentage: 0,
    completed_jobs: 0,
    hourly_rate: "Цена договорная",
    response_time: "24 часа",
  };

  const providerInfo = dashboardData?.provider_info || {
    name: "Мастер",
    profession: "Специалист",
    is_top_master: false,
    is_verified: false,
    location: "Город",
    is_online: false,
  };

  const skills = dashboardData?.skills || [];
  const reviews = dashboardData?.recent_reviews || [];
  const certificates = dashboardData?.certificates || [];
  const professionalInfo = dashboardData?.professional_info || {
    work_experience: "",
    education: "",
    education_years: "",
    languages: [],
    about: "",
  };

  return (
    <>
      <Header>
        <TopNav links={masterTopNav} />
        <div className="ms-auto flex items-center space-x-4">
          <ThemeSwitch />
          <ConfigDrawer />
          <ProfileDropdown />
        </div>
      </Header>

      <Main>
        <div className="space-y-6">
          {/* Master Profile Header */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <Avatar className="h-16 w-16">
                    <AvatarImage src={providerInfo.avatar} alt={providerInfo.name} />
                    <AvatarFallback>{providerInfo.name.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <div>
                    <h1 className="text-2xl font-bold">{providerInfo.name}</h1>
                    <p className="text-lg text-muted-foreground">{providerInfo.profession}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button>Выбрать</Button>
                  {providerInfo.is_top_master && (
                    <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                      ТОП мастер
                    </Badge>
                  )}
                  <Button variant="ghost" size="sm">
                    <Heart className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Statistics */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">{masterStats.total_orders}</div>
                  <p className="text-sm text-muted-foreground">Заказов</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">{masterStats.total_reviews}</div>
                  <p className="text-sm text-muted-foreground">Отзывов</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">{masterStats.on_time_percentage}%</div>
                  <p className="text-sm text-muted-foreground">В срок</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">{masterStats.repeat_customer_percentage}%</div>
                  <p className="text-sm text-muted-foreground">Повторно</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Work Examples - Portfolio */}
          {dashboardData?.portfolio && dashboardData.portfolio.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Примеры работ</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  {dashboardData.portfolio.map((item: any) => (
                    <div key={item.id} className="group cursor-pointer">
                      <div className="aspect-video overflow-hidden rounded-lg bg-muted">
                        <img
                          src={item.image_url}
                          alt={item.title}
                          className="h-full w-full object-cover transition-transform group-hover:scale-105"
                        />
                      </div>
                      <p className="mt-2 text-sm font-medium">{item.title}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Skills and Service Details */}
          <Card>
            <CardHeader>
              <CardTitle>Что умеет</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                {skills.map((skill) => (
                  <Badge key={skill.id} variant="outline">
                    {skill.name}
                  </Badge>
                ))}
              </div>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-lg font-semibold">{masterStats.completed_jobs} работ</div>
                  <p className="text-sm text-muted-foreground">Выполнено</p>
                </div>
                <div>
                  <div className="text-lg font-semibold">{masterStats.hourly_rate} за час</div>
                  <p className="text-sm text-muted-foreground">Стоимость</p>
                </div>
                <div>
                  <div className="text-lg font-semibold">{masterStats.response_time} скорость ответа</div>
                  <p className="text-sm text-muted-foreground">Время</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Client Reviews */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Отзывы клиентов</CardTitle>
                <div className="flex items-center space-x-2">
                  <div className="flex items-center space-x-1">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span className="text-sm font-medium">4.8</span>
                  </div>
                  <div className="w-20 h-2 bg-gray-200 rounded-full">
                    <div className="h-2 bg-blue-500 rounded-full" style={{ width: '80%' }}></div>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {reviews.map((review) => (
                <div key={review.id} className="flex space-x-3">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={review.client_avatar} alt={review.client_name} />
                    <AvatarFallback>{review.client_name.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">{review.client_name}</span>
                      <div className="flex">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`h-3 w-3 ${
                              i < review.rating
                                ? "fill-yellow-400 text-yellow-400"
                                : "text-gray-300"
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">{review.comment}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* About the Specialist */}
          <Card>
            <CardHeader>
              <CardTitle>О специалисте</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                {professionalInfo.about || "Информация о специалисте будет добавлена."}
              </p>
            </CardContent>
          </Card>

          {/* Professional Information */}
          <Card>
            <CardHeader>
              <CardTitle>Профессиональная информация</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-3">
                <Briefcase className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="font-medium">Опыт работы</p>
                  <p className="text-sm text-muted-foreground">{professionalInfo.work_experience || "Не указано"}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <GraduationCap className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="font-medium">Образование</p>
                  <p className="text-sm text-muted-foreground">{professionalInfo.education || "Не указано"}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Globe className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="font-medium">Языки</p>
                  <p className="text-sm text-muted-foreground">{professionalInfo.languages.join(", ") || "Не указано"}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Certificates */}
          <Card>
            <CardHeader>
              <CardTitle>Сертификаты</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {certificates.map((cert) => (
                  <Badge key={cert.id} variant="secondary">
                    <Award className="mr-1 h-3 w-3" />
                    {cert.name}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Call to Action */}
          <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20">
            <CardContent className="p-6">
              <div className="text-center">
                <h3 className="mb-2 text-lg font-semibold">Готов к работе</h3>
                <p className="mb-4 text-muted-foreground">
                  Расскажите о вашей задаче и получите профессиональную помощь
                </p>
                <Button size="lg" className="w-full sm:w-auto">
                  Рассказать о задаче
                </Button>
              </div>
            </CardContent>
          </Card>
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
    title: "Заказы",
    href: "/jobs",
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
    title: "Отзывы",
    href: "/reviews",
    isActive: false,
    disabled: false,
  },
  {
    title: "Профиль",
    href: "/settings/master",
    isActive: false,
    disabled: false,
  },
];
