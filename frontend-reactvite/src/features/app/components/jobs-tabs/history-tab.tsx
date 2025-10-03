import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Calendar, ChevronRight, MapPin } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import myApi from "@/lib/api/my-api";
import { Status30eEnum } from "@/lib/api/axios-client/api";

const HISTORY_JOBS_QUERY_KEY = 'history-jobs';

export function HistoryTab() {
  const historyQuery = useQuery({
    queryKey: [HISTORY_JOBS_QUERY_KEY],
    queryFn: async () => {
      const response = await myApi.v1SearchJobsList({
        ordering: '-created_at',
        page: 1,
        pageSize: 20,
        status: Status30eEnum.completed
      });
      return response.data;
    },
    staleTime: 30 * 1000, // 30 seconds
  });

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

  const getStatusBadge = (status: any) => {
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

  const historyJobs = historyQuery.data?.results || [];

  if (historyQuery.isLoading) {
    return (
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
    );
  }

  if (historyJobs.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-muted-foreground">История пуста</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {historyJobs.map((job: any) => (
        <Card key={job.id} className="hover:shadow-md transition-shadow border border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-semibold text-lg flex-1">{job.title || 'Untitled'}</h3>
              <div className="ml-2">
                {getStatusBadge(job.status)}
              </div>
            </div>

            <div className="text-blue-600 font-semibold text-lg mb-3">
              {job.budget_min && job.budget_max 
                ? `${job.budget_min.toLocaleString()} - ${job.budget_max.toLocaleString()} тг`
                : job.final_price 
                ? `${job.final_price.toLocaleString()} тг`
                : 'Цена договорная'
              }
            </div>

            <div className="space-y-2 mb-4">
              {job.service_date && (
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span>{formatDate(job.service_date)}</span>
                </div>
              )}
              {job.location && (
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <MapPin className="h-4 w-4" />
                  <span>{job.location}</span>
                </div>
              )}
            </div>

            <Button 
              className="w-full bg-blue-600 hover:bg-blue-700 text-white" 
              variant="outline"
            >
              Подробнее
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
