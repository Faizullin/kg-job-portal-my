import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import myApi from "@/lib/api/my-api";
import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { Calendar, ChevronRight, MapPin } from "lucide-react";

const ASSIGNMENTS_QUERY_KEY = 'assignments';

export function InProgressTab() {
  const assignmentsQuery = useQuery({
    queryKey: [ASSIGNMENTS_QUERY_KEY],
    queryFn: async () => {
      const response = await myApi.v1AssignmentsList({
        ordering: '-created_at',
        pageSize: 20,
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
      case 'assigned':
        return <Badge className="bg-purple-100 text-purple-800">Назначен</Badge>;
      case 'in_progress':
        return <Badge className="bg-yellow-100 text-yellow-800">В работе</Badge>;
      case 'completed':
        return <Badge className="bg-green-100 text-green-800">Завершен</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800">В работе</Badge>;
    }
  };

  const assignments = assignmentsQuery.data?.results || [];

  if (assignmentsQuery.isLoading) {
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

  if (assignments.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-muted-foreground">Нет заявок в работе</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {assignments.map((assignment: any) => (
        <Card key={assignment.id} className="hover:shadow-md transition-shadow border border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-semibold text-lg flex-1">{assignment.job?.title || 'Untitled'}</h3>
              <div className="ml-2">
                {getStatusBadge(assignment.status)}
              </div>
            </div>

            <div className="text-blue-600 font-semibold text-lg mb-3">
              {assignment.job?.budget_min && assignment.job?.budget_max
                ? `${assignment.job.budget_min.toLocaleString()} - ${assignment.job.budget_max.toLocaleString()} тг`
                : assignment.job?.final_price
                  ? `${assignment.job.final_price.toLocaleString()} тг`
                  : 'Цена договорная'
              }
            </div>

            <div className="space-y-2 mb-4">
              {assignment.job?.service_date && (
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span>{formatDate(assignment.job.service_date)}</span>
                </div>
              )}
              {assignment.job?.location && (
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <MapPin className="h-4 w-4" />
                  <span>{assignment.job.location}</span>
                </div>
              )}
            </div>

            <Button
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              variant="outline"
              asChild
            >
              <Link to={`/jobs/assginments/$assignmentId`} params={{ assignmentId: assignment.id }}>
                Подробнее
                <ChevronRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
