import { ConfigDrawer } from "@/components/config-drawer";
import { DataTable } from "@/components/data-table/data-table";
import { DataTableToolbar } from "@/components/data-table/data-table-toolbar";
import { useDataTable } from "@/components/data-table/use-data-table";
import { DeleteConfirmNiceDialog } from "@/components/dialogs/delete-confirm-dialog";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import NiceModal from "@/components/nice-modal/modal-context";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { Search } from "@/components/search";
import { ThemeSwitch } from "@/components/theme-switch";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { useDebounce } from "@/hooks/use-debounce";
import {
    JobApplicationStatusEnum,
  type JobApplication,
} from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";
import {
  Calendar,
  Eye,
  MoreHorizontal,
  SearchIcon,
  CheckCircle,
  XCircle,
  Clock,
  User,
  Trash2,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { Link } from "@tanstack/react-router";

export function EmployerApplicationsPage() {
  return (
    <>
      <Header fixed>
        <Search />
        <div className="ms-auto flex items-center space-x-4">
          <ThemeSwitch />
          <ConfigDrawer />
          <ProfileDropdown />
        </div>
      </Header>

      <Main>
        <RenderTable />
      </Main>
    </>
  );
}

const loadEmployerApplicationsQueryKey = 'employer-applications';

const RenderTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  const [parsedData, setParsedData] = useState<Array<JobApplication>>([]);
  const [parsedPagination, setParsedPagination] = useState({
    pageCount: 1,
  });

  const queryClient = useQueryClient();

  const loadEmployerApplicationsQuery = useQuery({
    queryKey: [loadEmployerApplicationsQueryKey, debouncedSearchQuery],
    queryFn: async () => {
      const response = await myApi.v1ApplicationsList({
        search: debouncedSearchQuery || undefined,
        page: 1,
        pageSize: 10,
      });
      return response.data;
    },
    staleTime: 0,
  });

  useEffect(() => {
    if (!loadEmployerApplicationsQuery.data) return;
    const parsed = loadEmployerApplicationsQuery.data.results || [];
    setParsedData(parsed);
    setParsedPagination({
      pageCount: Math.ceil(
        (loadEmployerApplicationsQuery.data.count || 0) / 10,
      ),
    });
  }, [loadEmployerApplicationsQuery.data]);

  const totalCount = parsedData.length;

  // Accept application mutation
  const acceptMutation = useMutation({
    mutationFn: async (applicationId: number) => {
      const response = await myApi.v1ApplicationsAccept({
        id: applicationId,
        jobApplicationRequest: {
          applicant: null,
          status: "accepted" as JobApplicationStatusEnum,
        }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadEmployerApplicationsQueryKey] });
      toast.success("Application accepted successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Failed to accept application");
    },
  });

  // Reject application mutation
  const rejectMutation = useMutation({
    mutationFn: async (applicationId: number) => {
      const response = await myApi.v1ApplicationsAcceptReject({
        id: applicationId,
        jobApplicationRequest: {
          applicant: null,
          status: "rejected" as JobApplicationStatusEnum,
        }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadEmployerApplicationsQueryKey] });
      toast.success("Application rejected successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Failed to reject application");
    },
  });

  const handleAccept = useCallback((application: JobApplication) => {
    if (application.status === "pending") {
      acceptMutation.mutate(application.id);
    }
  }, [acceptMutation]);

  const handleReject = useCallback((application: JobApplication) => {
    if (application.status === "pending") {
      rejectMutation.mutate(application.id);
    }
  }, [rejectMutation]);

  // Delete application mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => myApi.v1ApplicationsDestroy({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadEmployerApplicationsQueryKey] });
      toast.success("Application deleted successfully!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete application");
    },
  });
  const deleteMutationMutateAsync = deleteMutation.mutateAsync;
  const handleDeleteApplication = useCallback((application: JobApplication) => {
    NiceModal.show(DeleteConfirmNiceDialog, {
      args: {
        title: "Delete Application",
        desc: `Are you sure you want to delete this application for "${application.job.title}"? This action cannot be undone.`,
      }
    }).then((response) => {
      if (response.reason === "confirm") {
        deleteMutationMutateAsync(application.id);
      }
    })
  }, [deleteMutationMutateAsync]);

  const getStatusColor = useCallback((status?: JobApplicationStatusEnum) => {
    switch (status) {
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "accepted":
        return "bg-green-100 text-green-800";
      case "rejected":
        return "bg-red-100 text-red-800";
      case "withdrawn":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  }, []);

  const getStatusIcon = useCallback((status?: JobApplicationStatusEnum) => {
    switch (status) {
      case "pending":
        return <Clock className="h-4 w-4" />;
      case "accepted":
        return <CheckCircle className="h-4 w-4" />;
      case "rejected":
        return <XCircle className="h-4 w-4" />;
      case "withdrawn":
        return <XCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  }, []);

  const formatDate = useCallback((dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }, []);

  const formatBudget = useCallback((job: JobApplication['job']) => {
    if (job.budget_min && job.budget_max) {
      return `${job.budget_min} - ${job.budget_max} тг`;
    } else if (job.budget_min) {
      return `${job.budget_min} тг`;
    } else if (job.budget_max) {
      return `до ${job.budget_max} тг`;
    }
    return "Цена договорная";
  }, []);

  const columns = useMemo<ColumnDef<JobApplication, any>[]>(() => [
    {
      accessorKey: "id",
      header: "ID",
      cell: ({ row }) => (
        <a className="font-mono text-sm" href="#" onClick={(e) => {
          e.preventDefault();
        }}>
          #{row.getValue("id")}
        </a>
      ),
      meta: {
        variant: "number",
        label: "ID",
        className: ""
      }
    },
    {
      accessorKey: "job.title",
      header: "Job Title",
      cell: ({ row }) => {
        const job = row.original.job;
        return (
          <div className="max-w-[300px]">
            <div className="font-medium truncate">{job.title}</div>
            <div className="text-sm text-muted-foreground truncate">
              {job.location}
            </div>
            <div className="text-xs text-blue-600 truncate">
              {formatBudget(job)}
            </div>
          </div>
        );
      },
      meta: {
        variant: "text",
        placeholder: "Search jobs...",
        label: "Search",
        className: ""
      }
    },
    {
      accessorKey: "applicant",
      header: "Applicant",
      cell: ({ row }) => {
        const application = row.original;
        return (
          <div className="max-w-[200px]">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-muted-foreground" />
              <div className="truncate">
                <div className="font-medium text-sm">
                  Master #{application.applicant}
                </div>
                <div className="text-xs text-muted-foreground">
                  Applied {formatDate(application.applied_at)}
                </div>
              </div>
            </div>
          </div>
        );
      },
      meta: {
        variant: "text",
        label: "Applicant",
        className: ""
      }
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => {
        const status = row.original.status;
        return (
          <Badge className={getStatusColor(status)}>
            <div className="flex items-center gap-1">
              {getStatusIcon(status)}
              {status || "pending"}
            </div>
          </Badge>
        );
      },
      meta: {
        variant: "select",
        label: "Status",
        options: [
          { label: "Pending", value: "pending" },
          { label: "Accepted", value: "accepted" },
          { label: "Rejected", value: "rejected" },
          { label: "Withdrawn", value: "withdrawn" },
        ],
        className: ""
      }
    },
    {
      accessorKey: "applied_at",
      header: "Applied At",
      cell: ({ row }) => (
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <Calendar className="h-3 w-3" />
          <span>{formatDate(row.original.applied_at)}</span>
        </div>
      ),
      meta: {
        variant: "date",
        label: "Applied Date",
        className: ""
      }
    },
    {
      accessorKey: "job.service_date",
      header: "Service Date",
      cell: ({ row }) => {
        const job = row.original.job;
        if (job.service_date) {
          return (
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <Calendar className="h-3 w-3" />
              <span>{new Date(job.service_date).toLocaleDateString('ru-RU')}</span>
            </div>
          );
        }
        return <span className="text-muted-foreground">Not specified</span>;
      },
      meta: {
        variant: "date",
        label: "Service Date",
        className: ""
      }
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const application = row.original;
        const canAccept = application.status === JobApplicationStatusEnum.pending;
        const canReject = application.status === JobApplicationStatusEnum.pending;
        
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreHorizontal className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <Link 
                  to="/jobs/$jobId" 
                  params={{ jobId: application.job.id.toString() }} 
                  className="flex items-center gap-2"
                >
                  <Eye className="h-4 w-4" />
                  View Job
                </Link>
              </DropdownMenuItem>
              
              {canAccept && (
                <DropdownMenuItem 
                  onClick={() => handleAccept(application)}
                  className="flex items-center gap-2 text-green-600"
                >
                  <CheckCircle className="h-4 w-4" />
                  Accept
                </DropdownMenuItem>
              )}
              
              {canReject && (
                <DropdownMenuItem 
                  onClick={() => handleReject(application)}
                  className="flex items-center gap-2 text-red-600"
                >
                  <XCircle className="h-4 w-4" />
                  Reject
                </DropdownMenuItem>
              )}
              
              <DropdownMenuItem 
                onClick={() => handleDeleteApplication(application)}
                className="flex items-center gap-2 text-red-600"
              >
                <Trash2 className="h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ], [getStatusColor, getStatusIcon, formatDate, formatBudget, handleAccept, handleReject, handleDeleteApplication]);

  const { table } = useDataTable({
    data: parsedData,
    columns,
    pageCount: parsedPagination.pageCount,
    enableGlobalFilter: true,
    initialState: {
      sorting: [{ id: "id", desc: true }],
    },
  });

  if (loadEmployerApplicationsQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (loadEmployerApplicationsQuery.error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading applications</p>
        <Button onClick={() => loadEmployerApplicationsQuery.refetch()} className="mt-2">
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="-mx-4 flex-1 overflow-auto px-4 py-1 lg:flex-row lg:space-y-0 lg:space-x-12">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">Job Applications</h3>
            <p className="text-sm text-muted-foreground">
              {totalCount} application{totalCount !== 1 ? 's' : ''} found
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="relative flex-1 max-w-sm">
              <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search applications..."
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                className="pl-8 h-8"
              />
            </div>
          </div>
        </div>
        <DataTable table={table}>
          <DataTableToolbar table={table} />
        </DataTable>
      </div>
    </div>
  );
};
